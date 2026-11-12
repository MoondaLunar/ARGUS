package com.example.intelligence.config;

import com.example.intelligence.filter.PgpSignatureFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final PgpSignatureFilter pgpSignatureFilter;

    public SecurityConfig(PgpSignatureFilter pgpSignatureFilter) {
        this.pgpSignatureFilter = pgpSignatureFilter;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll())
            .addFilterBefore(pgpSignatureFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
