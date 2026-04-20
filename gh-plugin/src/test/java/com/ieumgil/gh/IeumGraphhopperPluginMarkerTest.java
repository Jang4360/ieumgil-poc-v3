package com.ieumgil.gh;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class IeumGraphhopperPluginMarkerTest {

    @Test
    void markerNameRemainsStable() {
        assertEquals("IeumGraphhopperPluginMarker", IeumGraphhopperPluginMarker.class.getSimpleName());
    }
}
