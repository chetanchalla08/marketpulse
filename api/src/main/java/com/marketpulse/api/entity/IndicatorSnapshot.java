package com.marketpulse.api.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

@Entity
@Table(name = "indicator_snapshots")
public class IndicatorSnapshot {

    @Id
    private Integer id;

    private String symbol;
    private LocalDateTime timestamp;
    private Double close;
    private Double volume;
    private Double rsi;
    private Double macd;
    private Double macdSignal;
    private Double macdHist;
    private Double vwap;
    private LocalDateTime createdAt;

    public Integer getId() {
        return id;
    }

    public String getSymbol() {
        return symbol;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public Double getClose() {
        return close;
    }

    public Double getVolume() {
        return volume;
    }

    public Double getRsi() {
        return rsi;
    }

    public Double getMacd() {
        return macd;
    }

    public Double getMacdSignal() {
        return macdSignal;
    }

    public Double getMacdHist() {
        return macdHist;
    }

    public Double getVwap() {
        return vwap;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
