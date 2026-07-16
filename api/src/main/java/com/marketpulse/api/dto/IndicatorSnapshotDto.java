package com.marketpulse.api.dto;

import com.marketpulse.api.entity.IndicatorSnapshot;

import java.time.LocalDateTime;

public record IndicatorSnapshotDto(
        Integer id,
        String symbol,
        LocalDateTime timestamp,
        Double close,
        Double volume,
        Double rsi,
        Double macd,
        Double macdSignal,
        Double macdHist,
        Double vwap
) {
    public static IndicatorSnapshotDto from(IndicatorSnapshot s) {
        return new IndicatorSnapshotDto(
                s.getId(), s.getSymbol(), s.getTimestamp(), s.getClose(), s.getVolume(),
                s.getRsi(), s.getMacd(), s.getMacdSignal(), s.getMacdHist(), s.getVwap()
        );
    }
}
