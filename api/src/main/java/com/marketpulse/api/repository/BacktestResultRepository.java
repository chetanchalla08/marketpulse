package com.marketpulse.api.repository;

import com.marketpulse.api.entity.BacktestResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.time.LocalDateTime;
import java.util.List;

public interface BacktestResultRepository extends JpaRepository<BacktestResult, Integer> {

    List<BacktestResult> findByRunAtOrderByRuleNameAscHorizonDaysAsc(LocalDateTime runAt);

    @Query("SELECT MAX(b.runAt) FROM BacktestResult b")
    LocalDateTime findLatestRunAt();

    @Query("SELECT DISTINCT b.runAt FROM BacktestResult b ORDER BY b.runAt DESC")
    List<LocalDateTime> findDistinctRunAtOrderByRunAtDesc();
}
