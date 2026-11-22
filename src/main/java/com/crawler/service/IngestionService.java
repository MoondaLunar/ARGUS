package com.crawler.service;

import com.crawler.model.*;
import com.crawler.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.BeanWrapperImpl;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.server.ResponseStatusException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.Supplier;

/** Evidence-preserving upserts. Each transaction commits before releasing the local lock. */
@Service
public class IngestionService {
    private final DocumentArtifactRepository documents;
    private final IntelligenceLinkRepository links;
    private final TransactionTemplate transaction;

    public IngestionService(DocumentArtifactRepository documents, IntelligenceLinkRepository links,
                            PlatformTransactionManager manager) {
        this.documents=documents; this.links=links; this.transaction=new TransactionTemplate(manager);
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new ResponseStatusException(HttpStatus.BAD_REQUEST, message);
    }
    private static boolean present(String text) { return text != null && !text.isBlank(); }

    private static void copyPresent(Object source, Object destination, String... protectedFields) {
        Set<String> ignored = new HashSet<>(Arrays.asList(protectedFields));
        var wrapper = new BeanWrapperImpl(source);
        for (var property : wrapper.getPropertyDescriptors()) {
            if (wrapper.isReadableProperty(property.getName()) && wrapper.getPropertyValue(property.getName()) == null)
                ignored.add(property.getName());
        }
        BeanUtils.copyProperties(source, destination, ignored.toArray(String[]::new));
    }

    private <T> T commitWithRetry(Supplier<T> operation) {
        try { return transaction.execute(status -> operation.get()); }
        catch (DataIntegrityViolationException collision) {
            // A competing process may have inserted the unique key. Retry in a fresh transaction.
            return transaction.execute(status -> operation.get());
        }
    }

    public synchronized DocumentArtifact document(DocumentArtifact incoming) {
        require(present(incoming.getIdentifier()) && incoming.getIdentifier().length() <= 2000, "Identifier required (max 2000 characters)");
        require(present(incoming.getSourceType()), "Source type required");
        return commitWithRetry(() -> {
            var existing = documents.findByIdentifier(incoming.getIdentifier()).orElseGet(DocumentArtifact::new);
            copyPresent(incoming, existing, "id", "discoveredAt");
            existing.setIndexedAt(java.time.LocalDateTime.now());
            return documents.saveAndFlush(existing);
        });
    }

    public synchronized IntelligenceLink link(IntelligenceLink incoming) {
        require(present(incoming.getEntityA()) && present(incoming.getEntityB()), "Both endpoints required");
        require(present(incoming.getLinkType()), "Link type required");
        require(incoming.getConfidence()!=null && Double.isFinite(incoming.getConfidence()) && incoming.getConfidence()>=0 && incoming.getConfidence()<=1, "Finite score in [0,1] required");
        if (!present(incoming.getEvidenceKey())) {
            // Legacy clients retain distinct observations instead of collapsing all evidence for a pair.
            incoming.setEvidenceKey(hash(String.join("\n", incoming.getEntityA(), incoming.getEntityB(),
                incoming.getLinkType(), Objects.toString(incoming.getSourceUrl(), ""),
                Objects.toString(incoming.getMetadataEvidence(), ""))));
        }
        require(incoming.getEvidenceKey().matches("[0-9a-f]{64}"), "Evidence key must be SHA-256 hex");
        return commitWithRetry(() -> {
            var existing = links.findByEvidenceKey(incoming.getEvidenceKey()).orElseGet(IntelligenceLink::new);
            copyPresent(incoming, existing, "id", "createdAt", "updatedAt");
            existing.setUpdatedAt(java.time.LocalDateTime.now());
            return links.saveAndFlush(existing);
        });
    }

    public static String hash(String value) {
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8))); }
        catch (java.security.NoSuchAlgorithmException impossible) { throw new IllegalStateException(impossible); }
    }
}
