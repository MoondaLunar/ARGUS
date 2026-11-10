package com.example.intelligence.service;

import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openpgp.*;
import org.bouncycastle.openpgp.jcajce.JcaPGPObjectFactory;
import org.bouncycastle.openpgp.operator.jcajce.JcaKeyFingerprintCalculator;
import org.bouncycastle.openpgp.operator.jcajce.JcaPGPContentVerifierBuilderProvider;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.security.Security;

@Service
public class SignatureVerificationService {

    @PostConstruct
    public void init() {
        Security.addProvider(new BouncyCastleProvider());
    }

    /**
     * Verifies a detached PGP signature against a raw payload.
     * 
     * @param payloadBytes The exact raw bytes received in the request body.
     * @param armoredSignature The armored signature string from the X-PGP-Signature header.
     * @param publicKeyBytes The raw bytes of your public_key.asc.
     */
    public boolean verifySignature(byte[] payloadBytes, String armoredSignature, byte[] publicKeyBytes) throws Exception {
        InputStream sigIn = PGPUtil.getDecoderStream(new ByteArrayInputStream(armoredSignature.getBytes()));
        JcaPGPObjectFactory pgpFact = new JcaPGPObjectFactory(sigIn);

        Object obj = pgpFact.nextObject();
        PGPSignatureList sigList;

        if (obj instanceof PGPSignatureList) {
            sigList = (PGPSignatureList) obj;
        } else {
            sigList = (PGPSignatureList) pgpFact.nextObject();
        }

        PGPSignature sig = sigList.get(0);

        // Load Public Key Collection
        PGPPublicKeyRingCollection pgpPub = new PGPPublicKeyRingCollection(
                PGPUtil.getDecoderStream(new ByteArrayInputStream(publicKeyBytes)),
                new JcaKeyFingerprintCalculator());

        PGPPublicKey publicKey = pgpPub.getPublicKey(sig.getKeyID());
        if (publicKey == null) {
            throw new IllegalArgumentException("Public key for signature not found in provided keyring.");
        }

        sig.init(new JcaPGPContentVerifierBuilderProvider().setProvider("BC"), publicKey);
        sig.update(payloadBytes);

        return sig.verify();
    }
}