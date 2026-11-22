package com.argus;
import com.intelligence.service.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.io.*;
import java.util.zip.*;
@SpringBootTest(properties={"spring.datasource.url=jdbc:h2:mem:export;DB_CLOSE_DELAY=-1", "spring.jpa.hibernate.ddl-auto=create-drop"})
class ExportTest {
    @Autowired EvidenceExportService export;
    @MockBean PgpSigningService signer;
    @Test void exportsExactPdfAndDetachedSignatureTogether() throws Exception {
        when(signer.signData(any())).thenReturn(new byte[]{1,2,3});
        byte[] bundle=export.generateSignedEvidencePdf();Map<String,byte[]> entries=new HashMap<>();
        try(var zip=new ZipInputStream(new ByteArrayInputStream(bundle))) {
            ZipEntry e;while((e=zip.getNextEntry())!=null)entries.put(e.getName(),zip.readAllBytes());
        }
        assertEquals(Set.of("evidence.pdf","evidence.pdf.sig"),entries.keySet());
        assertTrue(new String(entries.get("evidence.pdf"),0,4).equals("%PDF"));
        assertArrayEquals(new byte[]{1,2,3},entries.get("evidence.pdf.sig"));
        verify(signer).signData(entries.get("evidence.pdf"));
    }
}
