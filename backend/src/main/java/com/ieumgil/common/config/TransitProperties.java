package com.ieumgil.common.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "transit")
public record TransitProperties(
    @Valid Odsay odsay,
    @Valid Bims bims
) {

    public record Odsay(
        @NotBlank String apiKey,
        @NotBlank String baseUrl
    ) {
    }

    public record Bims(
        @NotBlank String serviceKey,
        @NotBlank String baseUrl
    ) {
    }
}
