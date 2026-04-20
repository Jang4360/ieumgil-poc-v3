package com.ieumgil;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class IeumgilBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(IeumgilBackendApplication.class, args);
    }
}
