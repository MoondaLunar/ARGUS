package com.argus;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * ARGUS entry point.
 *
 * The codebase grew in several packages (com.crawler, com.intelligence,
 * com.example.intelligence), so scanning starts at "com" rather than the
 * usual single base package.
 */
@SpringBootApplication(scanBasePackages = "com")
@EntityScan("com")
@EnableJpaRepositories("com")
public class ArgusApplication {
    public static void main(String[] args) {
        SpringApplication.run(ArgusApplication.class, args);
    }
}
