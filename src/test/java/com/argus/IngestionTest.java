package com.argus;

import com.crawler.model.*;
import com.crawler.repository.*;
import com.crawler.service.IngestionService;
import com.intelligence.service.CorroborationService;
import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import java.util.*;
import java.util.concurrent.*;

@SpringBootTest(properties={"spring.datasource.url=jdbc:h2:mem:rehab;DB_CLOSE_DELAY=-1", "spring.jpa.hibernate.ddl-auto=create-drop"})
class IngestionTest {
    @Autowired IngestionService service;
    @Autowired DocumentArtifactRepository documents;
    @Autowired IntelligenceLinkRepository links;
    @Autowired org.springframework.transaction.PlatformTransactionManager manager;
    @jakarta.persistence.PersistenceContext jakarta.persistence.EntityManager entityManager;

    DocumentArtifact doc(String identifier, String text) {
        var d=new DocumentArtifact("web",identifier,"html");d.setExtractedText(text);return d;
    }
    IntelligenceLink link(String key, double score) {
        var l=new IntelligenceLink("A","B",score,"candidate","https://example.test/a");
        l.setEvidenceKey(IngestionService.hash(key));return l;
    }
    @Test void repeatDocumentPreservesEnrichment() {
        String id="https://example.test/"+UUID.randomUUID();var first=doc(id,"old");first.setCameraMake("fixture");
        var stored=service.document(first);var updated=service.document(doc(id,"new"));
        assertEquals(stored.getId(),updated.getId());assertEquals("fixture",updated.getCameraMake());
        assertEquals("new",updated.getExtractedText());
    }
    @Test void documentRevisionsRetainPriorText() {
        String id="https://example.test/"+UUID.randomUUID();
        var first=service.document(doc(id,"original evidence"));
        service.document(doc(id,"corrected evidence"));
        new org.springframework.transaction.support.TransactionTemplate(manager).execute(status -> {
            var reader=org.hibernate.envers.AuditReaderFactory.get(entityManager);
            var revisions=reader.getRevisions(DocumentArtifact.class,first.getId());
            assertEquals(2,revisions.size());
            assertEquals("original evidence",reader.find(DocumentArtifact.class,first.getId(),revisions.get(0)).getExtractedText());
            return null;
        });
    }
    @Test void concurrentDocumentIngestHasOneIdentity() throws Exception {
        String id="https://example.test/"+UUID.randomUUID();var pool=Executors.newFixedThreadPool(4);
        try {
            List<Callable<Long>> tasks=new ArrayList<>();
            for(int i=0;i<8;i++) tasks.add(()->service.document(doc(id,"fixture")).getId());
            Set<Long> ids=new HashSet<>();for(var f:pool.invokeAll(tasks))ids.add(f.get());assertEquals(1,ids.size());
        } finally {pool.shutdownNow();}
    }
    @Test void distinctEvidenceSurvivesAndScoresCanBeCorrectedDown() {
        String key=UUID.randomUUID().toString();var first=service.link(link(key,.9));
        var corrected=service.link(link(key,.3));assertEquals(first.getId(),corrected.getId());assertEquals(.3,corrected.getConfidence());
        assertNotEquals(first.getId(),service.link(link(key+"second",.4)).getId());
    }
    @Test void rejectsMissingIdentifiersAndInvalidScores() {
        assertThrows(Exception.class,()->service.document(doc(null,"x")));
        assertThrows(Exception.class,()->service.link(link("bad",Double.NaN)));
    }
    @Test void duplicateHashNeverUpgradesCredibility() {
        var repository=mock(IntelligenceFindingRepository.class);var old=new IntelligenceFinding();
        when(repository.findByDataHash("same")).thenReturn(List.of(old));
        var incoming=new IntelligenceFinding();incoming.setDataHash("same");incoming.setInfoCredibility("6");
        new CorroborationService(repository).processCorroboration(incoming);
        assertEquals("6",incoming.getInfoCredibility());assertNull(incoming.getProbabilityPercentage());
    }
}
