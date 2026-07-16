package com.marketpulse.api.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

@Entity
@Table(name = "backtest_results")
public class BacktestResult {

    @Id
    private Integer id;

    private LocalDateTime runAt;
    private String ruleName;
    private Integer horizonDays;
    private Integer triggerCount;
    private Double winRatePct;
    private Double avgReturnPct;
    private LocalDateTime createdAt;

    public Integer getId() {
        return id;
    }

    public LocalDateTime getRunAt() {
        return runAt;
    }

    public String getRuleName() {
        return ruleName;
    }

    public Integer getHorizonDays() {
        return horizonDays;
    }

    public Integer getTriggerCount() {
        return triggerCount;
    }

    public Double getWinRatePct() {
        return winRatePct;
    }

    public Double getAvgReturnPct() {
        return avgReturnPct;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
