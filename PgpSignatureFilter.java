package com.example.intelligence.filter;

import com.example.intelligence.service.SignatureVerificationService;
import com.example.intelligence.util.CachedBodyHttpServletRequest;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

@Component
public class PgpSignatureFilter extends OncePerRequestFilter {

    private final SignatureVerificationService verificationService;
    private final String PUBLIC_KEY_PATH = "public_key.asc";

    public PgpSignatureFilter(SignatureVerificationService verificationService) {
        this.verificationService = verificationService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        if (request.getRequestURI().startsWith("/api")) {
            CachedBodyHttpServletRequest cachedRequest = new CachedBodyHttpServletRequest(request);
            String signatureArmored = cachedRequest.getHeader("X-PGP-Signature");

            if (signatureArmored == null || signatureArmored.isEmpty()) {
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing X-PGP-Signature header");
                return;
            }

            try {
                byte[] publicKey = Files.readAllBytes(Paths.get(PUBLIC_KEY_PATH));
                byte[] rawBody = cachedRequest.getCachedBody();

                if (verificationService.verifySignature(rawBody, signatureArmored, publicKey)) {
                    filterChain.doFilter(cachedRequest, response);
                } else {
                    response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid PGP Signature");
                }
            } catch (Exception e) {
                response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Signature error: " + e.getMessage());
            }
        } else {
            filterChain.doFilter(request, response);
        }
    }
}