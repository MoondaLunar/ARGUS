package com.intelligence.service;

import com.intelligence.audit.AuditRevisionEntity;
import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import com.lowagie.text.*;
import com.lowagie.text.pdf.PdfWriter;
import org.hibernate.envers.AuditReader;
import org.hibernate.envers.AuditReaderFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import java.io.ByteArrayOutputStream;
import java.util.List;

@Service
public class EvidenceExportService {

    @PersistenceContext
    private EntityManager entityManager;

    @Autowired
    private IntelligenceFindingRepository repository;

    @Autowired
    private PgpSigningService pgpSigningService;

    public byte[] generateSignedEvidencePdf() throws Exception {
        byte[] pdfBytes = generatePdfReport();
        return pgpSigningService.signData(pdfBytes);
    }

    private byte[] generatePdfReport() throws Exception {
        List<IntelligenceFinding> findings = repository.findAll();
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        Document document = new Document(PageSize.A4);
        PdfWriter.getInstance(document, out);
        document.open();

        Font titleFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18);
        Font sectionFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12);
        Font normalFont = FontFactory.getFont(FontFactory.HELVETICA, 10);
        Font auditFont = FontFactory.getFont(FontFactory.COURIER, 8);

        document.add(new Paragraph("OFFICIAL EVIDENCE REPORT - FBI OSINT SENTINEL", titleFont));
        document.add(new Paragraph("System Build: SENTINEL-V3.1.0", normalFont));
        document.add(new Paragraph("Export Timestamp: " + java.time.LocalDateTime.now(), normalFont));
        document.add(new Paragraph("\n"));

        AuditReader auditReader = AuditReaderFactory.get(entityManager);

        for (IntelligenceFinding finding : findings) {
            document.add(new Paragraph("ENTRY ID: " + finding.getId(), sectionFont));
            document.add(new Paragraph("Source URL: " + finding.getSourceUrl(), normalFont));
            document.add(new Paragraph("Description: " + finding.getDescription(), normalFont));
            
            document.add(new Paragraph("--- IMMUTABLE AUDIT TRAIL (ENVERS) ---", auditFont));
            
            List<Number> revisions = auditReader.getRevisions(IntelligenceFinding.class, finding.getId());
            for (Number revNum : revisions) {
                AuditRevisionEntity revEntity = auditReader.findRevision(AuditRevisionEntity.class, revNum);
                IntelligenceFinding historical = auditReader.find(IntelligenceFinding.class, finding.getId(), revNum);
                
                document.add(new Paragraph(String.format("Revision: %s | Date: %s | Build: %s", 
                    revNum, revEntity.getRevisionDate(), revEntity.getCrawlerBuild()), auditFont));
                document.add(new Paragraph("Content Hash: " + revEntity.getDataHash(), auditFont));
                document.add(new Paragraph("Historical Content: " + historical.toString(), auditFont));
                document.add(new Paragraph(" "));
            }
            document.add(new Paragraph("\n"));
        }

        document.close();
        return out.toByteArray();
    }
}