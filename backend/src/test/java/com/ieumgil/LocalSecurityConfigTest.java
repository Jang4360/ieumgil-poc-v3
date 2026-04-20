package com.ieumgil;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import com.ieumgil.common.config.LocalSecurityConfig;

@WebMvcTest
@AutoConfigureMockMvc
@ActiveProfiles("local")
@Import(LocalSecurityConfig.class)
class LocalSecurityConfigTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void permitsRequestsInLocalProfile() throws Exception {
        mockMvc.perform(get("/actuator/health"))
            .andExpect(status().isNotFound());
    }
}
