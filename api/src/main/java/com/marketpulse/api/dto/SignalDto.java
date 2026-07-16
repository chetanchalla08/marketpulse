package com.marketpulse.api.dto;

import com.marketpulse.api.entity.Signal;

import java.time.LocalDateTime;

public record SignalDto(
        Integer id,
        String symbol,
        LocalDateTime timestamp,
        String ruleName,
        Double closeAtSignal,
        String details
) {
    public static SignalDto from(Signal s) {
        return new SignalDto(s.getId(), s.getSymbol(), s.getTimestamp(), s.getRuleName(), s.getCloseAtSignal(), s.getDetails());
    }
}
