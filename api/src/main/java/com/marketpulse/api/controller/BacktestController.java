package com.marketpulse.api.controller;

import com.marketpulse.api.dto.BacktestResultDto;
import com.marketpulse.api.repository.BacktestResultRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;

@RestController
public class BacktestController {

    private final BacktestResultRepository backtestResultRepository;

    public BacktestController(BacktestResultRepository backtestResultRepository) {
        this.backtestResultRepository = backtestResultRepository;
    }

    @GetMapping("/api/backtest/results")
    public List<BacktestResultDto> getResults(@RequestParam(required = false) String runAt) {
        LocalDateTime targetRunAt = runAt != null
                ? LocalDateTime.parse(runAt)
                : backtestResultRepository.findLatestRunAt();

        if (targetRunAt == null) {
            return List.of();
        }

        return backtestResultRepository.findByRunAtOrderByRuleNameAscHorizonDaysAsc(targetRunAt).stream()
                .map(BacktestResultDto::from)
                .toList();
    }

    @GetMapping("/api/backtest/runs")
    public List<LocalDateTime> getRuns() {
        return backtestResultRepository.findDistinctRunAtOrderByRunAtDesc();
    }
}
