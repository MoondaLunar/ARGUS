package com.intelligence.service;

import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class CorroborationService {

    @Autowired
    private IntelligenceFindingRepository repository;

    /**
     * Analyzes a new finding against existing data. If the same data hash is found 
     * from a different source URL or agent, it upgrades the Info Credibility score.
     */
    public void processCorroboration(IntelligenceFinding newFinding) {
        List<IntelligenceFinding> existingMatches = repository.findByDataHash(newFinding.getDataHash());

        for (IntelligenceFinding existing : existingMatches) {
            // Rule: Independent corroboration requires a different source URL
            if (!existing.getSourceUrl().equals(newFinding.getSourceUrl())) {
                upgradeCredibility(newFinding, existing);
                
                // Human Intuition Pivot: Detect "Adversary Truth Mirroring"
                if (newFinding.getDeceptionFlag() || existing.getDeceptionFlag()) {
                    newFinding.setDescription(newFinding.getDescription() + 
                        " [DECINT ALERT: Truth Mirroring detected via Deceptive Source]");
                }

                // Detect Semantic Jitter (Shared truth, massaged wording)
                if ("SEMANTIC_JITTER".equals(newFinding.getType())) {
                    newFinding.setInfoCredibility("2"); // Upgrade to 'Probably True' due to intent matching
                    newFinding.setDescription(newFinding.getDescription() + " [SEMANTIC JITTER DETECTED: Intelligence content matches historical baseline]");
                }
            }
        }
    }

    private void upgradeCredibility(IntelligenceFinding incoming, IntelligenceFinding historical) {
        try {
            int currentScore = Integer.parseInt(incoming.getInfoCredibility());
            
            // Military logic: Independent corroboration improves credibility (lower number)
            // If matched on a different source, improve by 1 step, floor at 1 (Confirmed)
            if (currentScore > 1) {
                int upgradedScore = currentScore - 1;
                incoming.setInfoCredibility(String.valueOf(upgradedScore));
                
                // Update text description for reporting
                if (upgradedScore == 1) incoming.setConfidenceLevel("Confirmed (A1/B1)");
                else if (upgradedScore == 2) incoming.setConfidenceLevel("Probably True");
                
                incoming.setDescription(incoming.getDescription() + 
                    " [Corroborated by historical finding ID: " + historical.getId() + "]");
            }
        } catch (NumberFormatException e) {
            // Handle non-numeric Admiralty scores if necessary
        }
    }
}