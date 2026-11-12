package com.intelligence.service;

import org.bouncycastle.bcpg.BCPGOutputStream;
import org.bouncycastle.openpgp.*;
import org.bouncycastle.openpgp.operator.jcajce.JcaKeyFingerprintCalculator;
import org.bouncycastle.openpgp.operator.jcajce.JcaPGPContentSignerBuilder;
import org.bouncycastle.openpgp.operator.jcajce.JcePBESecretKeyDecryptorBuilder;
import org.springframework.stereotype.Service;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Iterator;

@Service
public class PgpSigningService {

    private final String SECRET_KEY_PATH = "secret_key.asc";
    private final String PASSPHRASE = "your_secure_passphrase"; // In production, use an env variable

    /**
     * Generates a PGP Detached Signature for the provided data.
     */
    public byte[] signData(byte[] data) throws Exception {
        InputStream keyIn = Files.newInputStream(Paths.get(SECRET_KEY_PATH));
        PGPSecretKey secretKey = readSecretKey(keyIn);
        
        PGPPrivateKey privateKey = secretKey.extractPrivateKey(
                new JcePBESecretKeyDecryptorBuilder().setProvider("BC").build(PASSPHRASE.toCharArray()));

        PGPSignatureGenerator signatureGenerator = new PGPSignatureGenerator(
                new JcaPGPContentSignerBuilder(secretKey.getPublicKey().getAlgorithm(), PGPUtil.SHA256).setProvider("BC"));

        signatureGenerator.init(PGPSignature.BINARY_DOCUMENT, privateKey);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        BCPGOutputStream bcOut = new BCPGOutputStream(out);

        signatureGenerator.update(data);
        signatureGenerator.generate().encode(bcOut);
        
        bcOut.close();
        return out.toByteArray();
    }

    private PGPSecretKey readSecretKey(InputStream input) throws Exception {
        PGPSecretKeyRingCollection pgpSec = new PGPSecretKeyRingCollection(
                PGPUtil.getDecoderStream(input), new JcaKeyFingerprintCalculator());

        Iterator<PGPSecretKeyRing> keyRingIter = pgpSec.getKeyRings();
        while (keyRingIter.hasNext()) {
            PGPSecretKeyRing keyRing = keyRingIter.next();
            Iterator<PGPSecretKey> keyIter = keyRing.getSecretKeys();
            while (keyIter.hasNext()) {
                PGPSecretKey key = keyIter.next();
                if (key.isSigningKey()) {
                    return key;
                }
            }
        }
        throw new IllegalArgumentException("Can't find signing key in key ring.");
    }
}