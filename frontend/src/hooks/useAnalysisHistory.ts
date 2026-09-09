import { useCallback, useEffect, useState } from "react";
import { ApiError, fetchAnalysisList } from "../api/client";
import type { AnalysisSummary } from "../types";

const PAGE_SIZE = 8;

interface HistoryState {
  items: AnalysisSummary[];
  total: number;
  offset: number;
  loading: boolean;
  error: string | null;
}

export function useAnalysisHistory() {
  const [state, setState] = useState<HistoryState>({
    items: [],
    total: 0,
    offset: 0,
    loading: false,
    error: null,
  });

  const load = useCallback(async (offset: number) => {
    setState((previous) => ({ ...previous, loading: true, error: null }));

    try {
      const response = await fetchAnalysisList(PAGE_SIZE, offset);
      setState({
        items: response.items,
        total: response.total,
        offset,
        loading: false,
        error: null,
      });
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "No se pudo cargar el historial.";
      setState((previous) => ({ ...previous, loading: false, error: message }));
    }
  }, []);

  useEffect(() => {
    load(0);
  }, [load]);

  const nextPage = useCallback(() => {
    if (state.offset + PAGE_SIZE < state.total) {
      load(state.offset + PAGE_SIZE);
    }
  }, [state.offset, state.total, load]);

  const previousPage = useCallback(() => {
    if (state.offset > 0) {
      load(Math.max(0, state.offset - PAGE_SIZE));
    }
  }, [state.offset, load]);

  const refresh = useCallback(() => load(0), [load]);

  return {
    ...state,
    pageSize: PAGE_SIZE,
    nextPage,
    previousPage,
    refresh,
    hasNext: state.offset + PAGE_SIZE < state.total,
    hasPrevious: state.offset > 0,
  };
}
