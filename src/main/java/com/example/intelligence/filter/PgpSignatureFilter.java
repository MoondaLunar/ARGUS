package com.example.intelligence.filter;

import com.example.intelligence.service.SignatureVerificationService;
import com.example.intelligence.util.CachedBodyHttpServletRequest;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Optional detached-PGP gate on the API.
 *
 * Signing every sweep with your own key is worth having when the API faces a
 * network. It is dead weight when the tool runs on your own machine, and a
 * filter that silently rejects every request because no key file exists is
 * worse than no filter. So: off unless argus.pgp.public-key points at a key.
 */
@Component
public class PgpSignatureFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(PgpSignatureFilter.class);

    private final SignatureVerificationService verificationService;

    @Value("${argus.pgp.public-key:}")
    private String publicKeyPath;

    private boolean warned = false;

    public PgpSignatureFilter(SignatureVerificationService verificationService) {
        this.verificationService = verificationService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        boolean enabled = publicKeyPath != null && !publicKeyPath.isBlank() && Files.exists(Paths.get(publicKeyPath));

        if (!enabled) {
            if (!warned) {
                log.info("PGP request gate is off (argus.pgp.public-key unset or missing). Set it to require X-PGP-Signature on /api/**.");
                warned = true;
            }
            filterChain.doFilter(request, response);
            return;
        }

        if (!request.getRequestURI().startsWith("/api")) {
            filterChain.doFilter(request, response);
            return;
        }

        CachedBodyHttpServletRequest cachedRequest = new CachedBodyHttpServletRequest(request);
        String signatureArmored = cachedRequest.getHeader("X-PGP-Signature");

        if (signatureArmored == null || signatureArmored.isEmpty()) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing X-PGP-Signature header");
            return;
        }

        try {
            byte[] publicKey = Files.readAllBytes(Path.of(publicKeyPath));
            byte[] rawBody = cachedRequest.getCachedBody();

            if (verificationService.verifySignature(rawBody, signatureArmored, publicKey)) {
                filterChain.doFilter(cachedRequest, response);
            } else {
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid PGP Signature");
            }
        } catch (Exception e) {
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Signature error: " + e.getMessage());
        }
    }
}
