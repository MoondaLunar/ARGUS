package com.argus;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.intelligence.controller.IntelligenceController;
import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import com.intelligence.service.CorroborationService;
import com.intelligence.service.EvidenceExportService;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class AssessmentTest {
    @Test void preservesSubmittedClaimsWithoutPromotingThemToAssessment() throws Exception {
        var repository=mock(IntelligenceFindingRepository.class);
        when(repository.save(any())).thenAnswer(call -> call.getArgument(0));
        var mapper=new ObjectMapper();
        var controller=new IntelligenceController(repository, mock(EvidenceExportService.class),
                mock(CorroborationService.class), mapper);
        var finding=new IntelligenceFinding();
        finding.setTimestamp(null); finding.setId(42L);
        finding.setDescription("Fixture research observation");
        finding.setSourceReliability("A"); finding.setInfoCredibility("1");
        finding.setDeceptionFlag(true); finding.setPersonaMatchScore(.99);
        finding.setProbabilityPercentage(99);
        assertEquals(200,controller.receiveFinding(finding,"client-hash","fixture").getStatusCode().value());
        var submitted=mapper.readTree(finding.getSubmittedAssessment());
        assertTrue(submitted.get("deceptionFlag").asBoolean());
        assertEquals("A",submitted.get("sourceReliability").asText());
        assertEquals(99,submitted.get("probabilityPercentage").asInt());
        assertNull(finding.getId()); assertNull(finding.getDeceptionFlag());
        assertNull(finding.getPersonaMatchScore()); assertNull(finding.getProbabilityPercentage());
        assertEquals("F",finding.getSourceReliability()); assertEquals("6",finding.getInfoCredibility());
        assertEquals("client-hash",finding.getSubmittedDataHash());
        assertNotEquals("client-hash",finding.getDataHash());
        assertEquals("Unassessed client submission",finding.getAnalyticStandard());
    }
}
