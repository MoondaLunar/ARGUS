package com.argus;
import com.example.intelligence.filter.PgpSignatureFilter;
import com.example.intelligence.service.SignatureVerificationService;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.*;
import org.springframework.test.util.ReflectionTestUtils;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
class PgpGateTest {
    @Test void missingConfiguredKeyFailsClosed() throws Exception {
        var filter=new PgpSignatureFilter(mock(SignatureVerificationService.class));
        ReflectionTestUtils.setField(filter,"publicKeyPath","/nonexistent/argus-test-key");
        var request=new MockHttpServletRequest("POST","/api/documents");
        var response=new MockHttpServletResponse();var chain=new MockFilterChain();
        filter.doFilter(request,response,chain);
        assertEquals(503,response.getStatus());assertNull(chain.getRequest());
    }
}
