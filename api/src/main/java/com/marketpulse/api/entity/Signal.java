package com.marketpulse.api.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

@Entity
@Table(name = "signals")
public class Signal {

    @Id
    private Integer id;

    private String symbol;
    private LocalDateTime timestamp;
    private String ruleName;
    private Double closeAtSignal;
    private String details;
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

    public String getRuleName() {
        return ruleName;
    }

    public Double getCloseAtSignal() {
        return closeAtSignal;
    }

    public String getDetails() {
        return details;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
