package com.marketpulse.api.repository;

import com.marketpulse.api.entity.Signal;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SignalRepository extends JpaRepository<Signal, Integer> {

    Page<Signal> findAllByOrderByTimestampDesc(Pageable pageable);

    Page<Signal> findBySymbolOrderByTimestampDesc(String symbol, Pageable pageable);

    Page<Signal> findByRuleNameOrderByTimestampDesc(String ruleName, Pageable pageable);

    Page<Signal> findBySymbolAndRuleNameOrderByTimestampDesc(String symbol, String ruleName, Pageable pageable);
}
