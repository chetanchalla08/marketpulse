package com.marketpulse.api.repository;

import com.marketpulse.api.entity.IndicatorSnapshot;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface IndicatorSnapshotRepository extends JpaRepository<IndicatorSnapshot, Integer> {

    Page<IndicatorSnapshot> findBySymbolOrderByTimestampDesc(String symbol, Pageable pageable);

    @Query(value = "SELECT DISTINCT ON (symbol) * FROM indicator_snapshots ORDER BY symbol, timestamp DESC", nativeQuery = true)
    List<IndicatorSnapshot> findLatestPerSymbol();

    @Query(value = "SELECT DISTINCT symbol FROM indicator_snapshots ORDER BY symbol", nativeQuery = true)
    List<String> findDistinctSymbols();
}
