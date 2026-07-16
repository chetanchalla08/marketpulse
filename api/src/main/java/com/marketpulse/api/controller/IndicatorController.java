package com.marketpulse.api.controller;

import com.marketpulse.api.dto.IndicatorSnapshotDto;
import com.marketpulse.api.repository.IndicatorSnapshotRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class IndicatorController {

    private final IndicatorSnapshotRepository indicatorSnapshotRepository;

    public IndicatorController(IndicatorSnapshotRepository indicatorSnapshotRepository) {
        this.indicatorSnapshotRepository = indicatorSnapshotRepository;
    }

    @GetMapping("/api/indicators/latest")
    public List<IndicatorSnapshotDto> getLatest() {
        return indicatorSnapshotRepository.findLatestPerSymbol().stream()
                .map(IndicatorSnapshotDto::from)
                .toList();
    }

    @GetMapping("/api/indicators/{symbol}")
    public List<IndicatorSnapshotDto> getHistory(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "100") int limit
    ) {
        return indicatorSnapshotRepository
                .findBySymbolOrderByTimestampDesc(symbol, PageRequest.of(0, limit))
                .map(IndicatorSnapshotDto::from)
                .getContent();
    }
}
