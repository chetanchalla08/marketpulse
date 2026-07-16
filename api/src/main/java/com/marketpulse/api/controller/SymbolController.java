package com.marketpulse.api.controller;

import com.marketpulse.api.repository.IndicatorSnapshotRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class SymbolController {

    private final IndicatorSnapshotRepository indicatorSnapshotRepository;

    public SymbolController(IndicatorSnapshotRepository indicatorSnapshotRepository) {
        this.indicatorSnapshotRepository = indicatorSnapshotRepository;
    }

    @GetMapping("/api/symbols")
    public List<String> getSymbols() {
        return indicatorSnapshotRepository.findDistinctSymbols();
    }
}
