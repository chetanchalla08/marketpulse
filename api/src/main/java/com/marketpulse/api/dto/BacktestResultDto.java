package com.marketpulse.api.dto;

import com.marketpulse.api.entity.BacktestResult;

import java.time.LocalDateTime;

public record BacktestResultDto(
        Integer id,
        LocalDateTime runAt,
        String ruleName,
        Integer horizonDays,
        Integer triggerCount,
        Double winRatePct,
        Double avgReturnPct
) {
    public static BacktestResultDto from(BacktestResult b) {
        return new BacktestResultDto(
                b.getId(), b.getRunAt(), b.getRuleName(), b.getHorizonDays(),
                b.getTriggerCount(), b.getWinRatePct(), b.getAvgReturnPct()
        );
    }
}
