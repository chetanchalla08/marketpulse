package com.marketpulse.api.controller;

import com.marketpulse.api.dto.SignalDto;
import com.marketpulse.api.entity.Signal;
import com.marketpulse.api.repository.SignalRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SignalController {

    private final SignalRepository signalRepository;

    public SignalController(SignalRepository signalRepository) {
        this.signalRepository = signalRepository;
    }

    @GetMapping("/api/signals")
    public Page<SignalDto> getSignals(
            @RequestParam(required = false) String symbol,
            @RequestParam(required = false) String ruleName,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Signal> result;

        if (symbol != null && ruleName != null) {
            result = signalRepository.findBySymbolAndRuleNameOrderByTimestampDesc(symbol, ruleName, pageable);
        } else if (symbol != null) {
            result = signalRepository.findBySymbolOrderByTimestampDesc(symbol, pageable);
        } else if (ruleName != null) {
            result = signalRepository.findByRuleNameOrderByTimestampDesc(ruleName, pageable);
        } else {
            result = signalRepository.findAllByOrderByTimestampDesc(pageable);
        }

        return result.map(SignalDto::from);
    }
}
