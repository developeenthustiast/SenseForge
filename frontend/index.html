import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { AlertTriangle, Activity, Brain, Shield, TrendingUp, TrendingDown, Zap, Clock, CheckCircle, XCircle, AlertCircle, Filter } from 'lucide-react';

// API Configuration
const API_BASE = 'http://localhost:8000';

// Design tokens & helpers for consistent styling
const ui = {
  shell: 'bg-slate-900/50 backdrop-blur-sm border border-slate-800/50 rounded-xl',
  surface: 'bg-slate-800/30 border border-slate-700/40 rounded-xl',
  focusRing: 'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500',
  textMuted: 'text-slate-400'
};

const translations = {
  en: {
    meta: {
      nativeName: 'English',
      currency: 'USD'
    },
    a11y: {
      localeSwitcher: 'Select interface language',
      logsFilter: 'Filter logs',
      skeletons: {
        currentState: 'Current state loading',
        prediction: 'Prediction loading',
        chart: 'Prediction chart loading',
        health: 'Component health loading'
      }
    },
    notifications: {
      healthError: 'Unable to reach system status endpoint',
      analysisSuccess: 'Risk analysis completed',
      analysisFailure: 'Risk analysis failed',
      analysisFailureDetailed: 'Risk analysis failed. Check logs for details.'
    },
    status: {
      checking: 'Checking...',
      unreachable: 'Unable to reach system status',
      unknown: 'Unknown status',
      map: {
        healthy: 'Healthy',
        degraded: 'Degraded',
        unhealthy: 'Unhealthy'
      }
    },
    header: {
      tagline: 'Institutional Liquidity Risk Oracle',
      localeLabel: 'Locale',
      mode: {
        mock: '🧪 Demo Mode',
        live: '🔴 Live'
      }
    },
    nav: {
      overview: { label: 'Overview', description: 'Top-level liquidity intelligence' },
      analysis: { label: 'Risk Analysis', description: 'Deep dive into proposals and predictions' },
      agents: { label: 'Tri-Agent System', description: 'Operational view of autonomous agents' },
      monitoring: { label: 'Monitoring', description: 'System health and telemetry' }
    },
    overview: {
      hero: {
        currentLiquidity: {
          label: 'Current Liquidity',
          description: 'Depth across monitored venues',
          placeholder: '$9.5M',
          trend: '+2.3%'
        },
        predictedRisk: {
          label: 'Predicted Risk',
          description: 'JEPA risk posture',
          placeholder: 'SAFE'
        },
        volatilityIndex: {
          label: 'Volatility Index',
          description: '24h realized volatility',
          placeholder: '0.52',
          trend: '-5.2%'
        },
        confidence: {
          label: 'Confidence',
          description: 'JEPA certainty score',
          placeholder: '87%'
        }
      },
      quickAnalysis: {
        title: 'Quick Risk Analysis',
        description: 'Run JEPA-based assessments on the latest liquidity snapshot',
        buttonIdle: 'Run Analysis',
        buttonBusy: 'Analyzing...',
        statusFallback: 'Status unavailable',
        currentStateLabel: 'Current State',
        predictionLabel: 'JEPA Prediction',
        fields: {
          liquidity: 'Liquidity Depth',
          volatility: 'Volatility',
          riskScore: 'Risk Score',
          riskLevel: 'Risk Level',
          recommendedAction: 'Recommended Action'
        }
      },
      chart: {
        title: 'Liquidity Predictions',
        description: 'Comparing current vs predicted liquidity depth',
        emptyDescription: 'Run an analysis to unlock prediction history'
      }
    },
    analysis: {
      title: 'Deep Risk Analysis',
      description: 'Submit targeted contexts for the tri-agent pipeline',
      fields: {
        proposalId: 'Proposal ID (Optional)',
        proposalPlaceholder: 'PROP-123',
        contextLabel: 'Analysis Context',
        contextPlaceholder: 'Debt ceiling increase proposal'
      },
      buttonIdle: 'Run Deep Analysis',
      buttonBusy: 'Analyzing Market Conditions...',
      cards: {
        jepa: 'JEPA Model',
        strategist: 'Strategist',
        auditor: 'Auditor',
        prediction: 'Prediction',
        change: 'Change',
        confidence: 'Confidence',
        approved: 'Approved',
        rejected: 'Rejected'
      }
    },
    agents: {
      title: 'Tri-Agent Workflow',
      description: 'Operational telemetry across Analyst, JEPA Brain, and Strategist',
      analyst: {
        name: 'The Analyst',
        role: 'Perception Layer',
        description: 'Ingests and normalizes on-chain data from Cambrian',
        metrics: ['5 events/sec', '99.9% uptime']
      },
      brain: {
        name: 'The Brain (JEPA)',
        role: 'Predictive Model',
        description: 'Predicts future liquidity using causal understanding',
        metrics: ['87% confidence', '16D latent space']
      },
      strategist: {
        name: 'The Strategist',
        role: 'Risk Reasoning',
        description: 'Interprets predictions using Ambient LLM',
        metrics: ['<200ms response', 'Natural language']
      }
    },
    logs: {
      title: 'Real-Time Agent Logs',
      description: 'Traceability feed for Analyst, Strategist, and Auditor decisions',
      empty: 'No logs match this filter yet.',
      filter: {
        all: 'All',
        success: 'Success',
        error: 'Errors',
        info: 'Info'
      }
    },
    monitoring: {
      title: 'System Health',
      description: 'Component uptime and readiness',
      modelPerformance: 'Model Performance',
      responseTimes: 'Response Times',
      metrics: {
        title: 'Prediction Metrics',
        description: 'Live accuracy and training telemetry',
        fields: {
          count: 'Completed Predictions',
          accuracy: 'Accuracy',
          mae: 'Mean Absolute Error',
          rmse: 'Root Mean Squared Error',
          epochs: 'Training Epochs',
          currentLoss: 'Current Loss',
          improvement: 'Improvement'
        },
        recentTitle: 'Recent Predictions',
        recentDescription: 'Latest JEPA outputs vs actuals',
        empty: 'No predictions recorded yet.',
        error: 'Unable to load metrics at this time.'
      }
    },
    footer: {
      summary: 'SenseForge v2.1 | Enterprise Risk Oracle',
      modePrefix: 'Mode:',
      uptime: 'Uptime: 99.9%',
      compliance: 'A2A Compliant'
    }
  }
};

const availableLocales = Object.entries(translations).map(([code, data]) => ({
  code,
  label: data.meta?.nativeName || code.toUpperCase()
}));

const createFormatters = (locale, currency) => ({
  currencyCompact: new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
    notation: 'compact'
  }),
  currency: new Intl.NumberFormat(locale, { style: 'currency', currency, maximumFractionDigits: 2 }),
  percent: new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0 }),
  time: (value) => new Date(value).toLocaleTimeString(locale)
});

const StatCard = ({ label, value, icon: Icon, trend, color = 'emerald', description }) => (
  <article className={`${ui.shell} p-6`} aria-live="polite">
    <div className="flex items-start justify-between mb-3">
      <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center`}>
        <Icon className={`w-5 h-5 text-${color}-400`} aria-hidden="true" />
      </div>
      {trend && (
        <span
          className={`text-xs px-2 py-1 rounded-full ${
            trend.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
          }`}
        >
          {trend}
        </span>
      )}
    </div>
    <div className="text-2xl font-bold text-slate-100 mb-1" aria-live="polite">{value}</div>
    <div className={`text-sm ${ui.textMuted}`}>{description || label}</div>
  </article>
);

const SectionShell = ({ id, title, description, actions, children, ariaBusy = false }) => (
  <section
    id={id}
    aria-labelledby={`${id}-title`}
    aria-describedby={description ? `${id}-description` : undefined}
    aria-busy={ariaBusy}
    className={`${ui.shell} p-6`}
  >
    <div className="flex items-center justify-between mb-6 gap-4">
      <div>
        <h2 id={`${id}-title`} className="text-xl font-bold text-slate-100">
          {title}
        </h2>
        {description && (
          <p id={`${id}-description`} className={`text-sm ${ui.textMuted}`}>
            {description}
          </p>
        )}
      </div>
      {actions}
    </div>
    {children}
  </section>
);

const SkeletonBlock = ({ className = '', label }) => (
  <div
    className={`animate-pulse rounded-lg bg-slate-800/40 border border-slate-800/60 ${className}`}
    aria-label={label || 'Loading'}
    role="status"
  />
);

const Toast = ({ type = 'info', message, onClose }) => {
  const colors = {
    success: 'bg-emerald-500/10 text-emerald-200 border-emerald-400/40',
    error: 'bg-rose-500/10 text-rose-100 border-rose-400/40',
    info: 'bg-slate-800/60 text-slate-100 border-slate-600/60'
  };

  return (
    <div
      className={`fixed top-6 right-6 min-w-[280px] px-4 py-3 border rounded-lg shadow-xl backdrop-blur ${colors[type]}`}
      role="status"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 text-sm">{message}</div>
        <button
          onClick={onClose}
          className={`text-xs uppercase tracking-wide ${ui.focusRing}`}
        >
          Close
        </button>
      </div>
    </div>
  );
};

const SenseForgeDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [systemStatusKey, setSystemStatusKey] = useState('checking');
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [agentLogs, setAgentLogs] = useState([]);
  const [logFilter, setLogFilter] = useState('all');
  const [toast, setToast] = useState(null);
  const [healthErrorNotified, setHealthErrorNotified] = useState(false);
  const [locale, setLocale] = useState('en');
  const [metricsData, setMetricsData] = useState(null);
  const [metricsError, setMetricsError] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(true);
  const tabListId = 'senseforge-primary-tabs';

  const localeConfig = translations[locale] ?? translations.en;
  const formatters = useMemo(
    () => createFormatters(locale, localeConfig.meta.currency),
    [locale, localeConfig.meta.currency]
  );

  const tabs = useMemo(() => ([
    { id: 'overview', label: localeConfig.nav.overview.label, description: localeConfig.nav.overview.description, icon: Activity },
    { id: 'analysis', label: localeConfig.nav.analysis.label, description: localeConfig.nav.analysis.description, icon: AlertTriangle },
    { id: 'agents', label: localeConfig.nav.agents.label, description: localeConfig.nav.agents.description, icon: Zap },
    { id: 'monitoring', label: localeConfig.nav.monitoring.label, description: localeConfig.nav.monitoring.description, icon: TrendingUp }
  ]), [localeConfig.nav]);

  const statusMessage = localeConfig.status.map[systemStatusKey] || localeConfig.status.unknown;
  const modeLabel = systemHealth?.mode === 'mock' ? localeConfig.header.mode.mock : localeConfig.header.mode.live;
  const toastMessages = localeConfig.notifications;

  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type });
  }, []);

  // Fetch system health
  const fetchHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setSystemHealth(data);
      setSystemStatusKey(data.status ?? 'unknown');
      setHealthErrorNotified(false);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemStatusKey('unreachable');
      if (!healthErrorNotified) {
        showToast(toastMessages.healthError, 'error');
        setHealthErrorNotified(true);
      }
    }
  }, [healthErrorNotified, showToast, toastMessages.healthError]);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(null), 5000);
    return () => clearTimeout(timer);
  }, [toast]);

  const fetchDashboardMetrics = useCallback(async () => {
    try {
      setMetricsLoading(true);
      const response = await fetch(`${API_BASE}/dashboard-metrics`);
      if (!response.ok) {
        throw new Error('metrics_unavailable');
      }
      const data = await response.json();
      setMetricsData(data);
      setMetricsError(null);
    } catch (error) {
      console.error('Metrics load failed:', error);
      setMetricsError(localeConfig.monitoring.metrics.error);
    } finally {
      setMetricsLoading(false);
    }
  }, [localeConfig.monitoring.metrics.error]);

  // Run risk analysis
  const runAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'Analyze current liquidity risk for governance proposals',
          metadata: { source: 'dashboard', timestamp: new Date().toISOString() }
        })
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        const analysis = result.data.analysis;
        setCurrentAnalysis(analysis);
        setAnalysisError(null);
        
        // Add to historical data
        setHistoricalData(prev => [...prev, {
          timestamp: new Date().toISOString(),
          predicted: analysis.prediction.predicted_liquidity,
          current: analysis.current_state.liquidity_depth,
          risk: analysis.risk_assessment.risk_level
        }].slice(-20));
        
        // Add log entry
        addLog('Analysis', `${localeConfig.analysis.cards.prediction}: ${analysis.risk_assessment.risk_level}`, 'success');
        showToast(toastMessages.analysisSuccess, 'success');
      } else {
        setAnalysisError(result.error?.message || toastMessages.analysisFailure);
        showToast(toastMessages.analysisFailure, 'error');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysisError(error.message);
      addLog('Error', error.message, 'error');
      showToast(toastMessages.analysisFailureDetailed, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const addLog = (component, message, type = 'info') => {
    setAgentLogs(prev => [{
      id: Date.now(),
      timestamp: new Date().toISOString(),
      component,
      message,
      type
    }, ...prev].slice(0, 50));
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  useEffect(() => {
    fetchDashboardMetrics();
    const interval = setInterval(fetchDashboardMetrics, 15000);
    return () => clearInterval(interval);
  }, [fetchDashboardMetrics]);

  const getRiskColor = (level) => {
    switch (level) {
      case 'SAFE': return 'text-emerald-500';
      case 'WARNING': return 'text-amber-500';
      case 'CRITICAL': return 'text-rose-500';
      default: return 'text-gray-500';
    }
  };

  const getRiskBg = (level) => {
    switch (level) {
      case 'SAFE': return 'bg-emerald-500/10 border-emerald-500/30';
      case 'WARNING': return 'bg-amber-500/10 border-amber-500/30';
      case 'CRITICAL': return 'bg-rose-500/10 border-rose-500/30';
      default: return 'bg-gray-500/10 border-gray-500/30';
    }
  };

  const filteredLogs = useMemo(() => {
    if (logFilter === 'all') return agentLogs;
    return agentLogs.filter(log => log.type === logFilter);
  }, [agentLogs, logFilter]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800/50 bg-slate-950/60 backdrop-blur-xl" role="banner">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                  SenseForge
                </h1>
                <p className="text-xs text-slate-400">{localeConfig.header.tagline}</p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-4" role="status" aria-live="polite">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-700/50">
                <div className={`w-2 h-2 rounded-full ${systemHealth?.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
                <span className="text-sm text-slate-300">
                  {statusMessage}
                </span>
              </div>
              <div className="text-sm text-slate-400" aria-label="environment mode">
                {modeLabel}
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-300" aria-label={localeConfig.a11y.localeSwitcher}>
                {localeConfig.header.localeLabel}
                <select
                  value={locale}
                  onChange={(event) => setLocale(event.target.value)}
                  className={`bg-slate-900/60 border border-slate-700/60 rounded-lg px-3 py-1 text-slate-200 ${ui.focusRing}`}
                >
                  {availableLocales.map(({ code, label }) => (
                    <option key={code} value={code}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-slate-800/50 bg-slate-900/40 backdrop-blur-sm" aria-label="Primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div
            className="flex flex-wrap gap-1"
            role="tablist"
            aria-orientation="horizontal"
            id={tabListId}
          >
            {tabs.map(tab => (
              <button
                key={tab.id}
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`${tab.id}-panel`}
                id={`${tab.id}-tab`}
                onClick={() => setActiveTab(tab.id)}
                aria-label={`${tab.label}: ${tab.description}`}
                className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-300 bg-indigo-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
                } ${ui.focusRing}`}
              >
                <tab.icon className="w-4 h-4" aria-hidden="true" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8" aria-live="polite">
        {activeTab === 'overview' && (
          <div
            id="overview-panel"
            role="tabpanel"
            aria-labelledby="overview-tab"
            className="space-y-6"
          >
            {/* Hero Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              {[
                {
                  label: localeConfig.overview.hero.currentLiquidity.label,
                  value: currentAnalysis
                    ? formatters.currencyCompact.format(currentAnalysis.current_state.liquidity_depth)
                    : localeConfig.overview.hero.currentLiquidity.placeholder,
                  icon: TrendingUp,
                  trend: localeConfig.overview.hero.currentLiquidity.trend,
                  color: 'emerald',
                  description: localeConfig.overview.hero.currentLiquidity.description
                },
                {
                  label: localeConfig.overview.hero.predictedRisk.label,
                  value: currentAnalysis?.risk_assessment.risk_level || localeConfig.overview.hero.predictedRisk.placeholder,
                  icon: Shield,
                  color: currentAnalysis ? currentAnalysis.risk_assessment.risk_level.toLowerCase() : 'emerald',
                  description: localeConfig.overview.hero.predictedRisk.description
                },
                {
                  label: localeConfig.overview.hero.volatilityIndex.label,
                  value: currentAnalysis ? currentAnalysis.current_state.volatility_index.toFixed(2) : localeConfig.overview.hero.volatilityIndex.placeholder,
                  icon: Activity,
                  trend: localeConfig.overview.hero.volatilityIndex.trend,
                  color: 'amber',
                  description: localeConfig.overview.hero.volatilityIndex.description
                },
                {
                  label: localeConfig.overview.hero.confidence.label,
                  value: currentAnalysis ? formatters.percent.format(currentAnalysis.prediction.confidence) : localeConfig.overview.hero.confidence.placeholder,
                  icon: CheckCircle,
                  color: 'indigo',
                  description: localeConfig.overview.hero.confidence.description
                }
              ].map((stat, idx) => (
                <StatCard key={idx} {...stat} />
              ))}
            </div>

            {/* Quick Analysis */}
            <SectionShell
              id="quick-analysis"
              title={localeConfig.overview.quickAnalysis.title}
              description={localeConfig.overview.quickAnalysis.description}
              ariaBusy={isAnalyzing}
              actions={null}
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className={`text-sm ${ui.textMuted}`}>{statusMessage}</p>
                </div>
                <button
                  onClick={runAnalysis}
                  disabled={isAnalyzing}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition-all flex items-center gap-2"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      {localeConfig.overview.quickAnalysis.buttonBusy}
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      {localeConfig.overview.quickAnalysis.buttonIdle}
                    </>
                  )}
                </button>
              </div>

              {analysisError && (
                <div className="mb-4 p-4 rounded-lg border border-rose-500/40 bg-rose-500/10 text-rose-200" role="alert">
                  {analysisError}
                </div>
              )}

              {!currentAnalysis && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <SkeletonBlock className="h-36" label={localeConfig.a11y.skeletons.currentState} />
                  <SkeletonBlock className="h-36" label={localeConfig.a11y.skeletons.prediction} />
                </div>
              )}

              {currentAnalysis && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-3">{localeConfig.overview.quickAnalysis.currentStateLabel}</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                        <span className="text-slate-300">{localeConfig.overview.quickAnalysis.fields.liquidity}</span>
                        <span className="font-mono text-emerald-400">
                          ${(currentAnalysis.current_state.liquidity_depth / 1e6).toFixed(2)}M
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                        <span className="text-slate-300">{localeConfig.overview.quickAnalysis.fields.volatility}</span>
                        <span className="font-mono text-amber-400">
                          {currentAnalysis.current_state.volatility_index.toFixed(3)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                        <span className="text-slate-300">{localeConfig.overview.quickAnalysis.fields.riskScore}</span>
                        <span className="font-mono text-rose-400">
                          {currentAnalysis.current_state.governance_risk_score.toFixed(3)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-3">{localeConfig.overview.quickAnalysis.predictionLabel}</h3>
                    <div className={`p-4 rounded-xl border ${getRiskBg(currentAnalysis.risk_assessment.risk_level)}`}>
                      <div className="flex items-center gap-3 mb-4">
                        <AlertTriangle className={`w-8 h-8 ${getRiskColor(currentAnalysis.risk_assessment.risk_level)}`} />
                        <div>
                          <div className={`text-2xl font-bold ${getRiskColor(currentAnalysis.risk_assessment.risk_level)}`}>
                            {currentAnalysis.risk_assessment.risk_level}
                          </div>
                          <div className="text-sm text-slate-400">{localeConfig.overview.quickAnalysis.fields.riskLevel}</div>
                        </div>
                      </div>
                      <div className="text-sm text-slate-300 mb-3">
                        {currentAnalysis.risk_assessment.reasoning}
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">{localeConfig.overview.quickAnalysis.fields.recommendedAction}</span>
                        <span className="font-medium text-indigo-400">
                          {currentAnalysis.risk_assessment.recommended_action}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </SectionShell>

            {/* Prediction Chart */}
            {historicalData.length > 0 ? (
              <SectionShell
                id="predictions"
                title={localeConfig.overview.chart.title}
                description={localeConfig.overview.chart.description}
              >
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={historicalData}>
                    <defs>
                      <linearGradient id="current" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="predicted" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#64748b"
                      tick={{ fill: '#94a3b8' }}
                      tickFormatter={(v) => new Date(v).toLocaleTimeString()}
                    />
                    <YAxis 
                      stroke="#64748b"
                      tick={{ fill: '#94a3b8' }}
                      tickFormatter={(v) => `$${(v / 1e6).toFixed(1)}M`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '0.5rem'
                      }}
                      labelStyle={{ color: '#cbd5e1' }}
                    />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="current" 
                      stroke="#10b981" 
                      fill="url(#current)"
                      strokeWidth={2}
                      name="Current Liquidity"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="predicted" 
                      stroke="#6366f1" 
                      fill="url(#predicted)"
                      strokeWidth={2}
                      name="Predicted Liquidity"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </SectionShell>
            ) : (
              <SectionShell
                id="predictions-empty"
                title={localeConfig.overview.chart.title}
                description={localeConfig.overview.chart.emptyDescription}
              >
                <SkeletonBlock className="h-48" label={localeConfig.a11y.skeletons.chart} />
              </SectionShell>
            )}
          </div>
        )}

        {activeTab === 'analysis' && (
          <div
            id="analysis-panel"
            role="tabpanel"
            aria-labelledby="analysis-tab"
            className="space-y-6"
          >
            <SectionShell
              id="deep-analysis"
              title={localeConfig.analysis.title}
              description={localeConfig.analysis.description}
              ariaBusy={isAnalyzing}
            >
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    {localeConfig.analysis.fields.proposalId}
                  </label>
                  <input
                    type="text"
                    placeholder={localeConfig.analysis.fields.proposalPlaceholder}
                    className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    {localeConfig.analysis.fields.contextLabel}
                  </label>
                  <input
                    type="text"
                    placeholder={localeConfig.analysis.fields.contextPlaceholder}
                    className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  />
                </div>
              </div>

              <button
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition-all"
              >
                {isAnalyzing ? localeConfig.analysis.buttonBusy : localeConfig.analysis.buttonIdle}
              </button>
            </div>

            {currentAnalysis && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className={`${ui.shell} p-6`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-semibold text-slate-100">{localeConfig.analysis.cards.jepa}</h3>
                  </div>
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="text-slate-400">{localeConfig.analysis.cards.prediction}</span>
                      <div className="font-mono text-indigo-400 mt-1">
                        ${(currentAnalysis.prediction.predicted_liquidity / 1e6).toFixed(2)}M
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400">{localeConfig.analysis.cards.change}</span>
                      <div className={`font-mono mt-1 ${currentAnalysis.prediction.change_percent < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {currentAnalysis.prediction.change_percent.toFixed(2)}%
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400">{localeConfig.analysis.cards.confidence}</span>
                      <div className="font-mono text-amber-400 mt-1">
                        {(currentAnalysis.prediction.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800/50 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold text-slate-100">{localeConfig.analysis.cards.strategist}</h3>
                  </div>
                  <div className={`p-3 rounded-lg ${getRiskBg(currentAnalysis.risk_assessment.risk_level)} mb-3`}>
                    <div className={`font-bold mb-1 ${getRiskColor(currentAnalysis.risk_assessment.risk_level)}`}>
                      {currentAnalysis.risk_assessment.risk_level}
                    </div>
                    <div className="text-xs text-slate-400">
                      {currentAnalysis.risk_assessment.recommended_action}
                    </div>
                  </div>
                  <p className="text-sm text-slate-300">
                    {currentAnalysis.risk_assessment.reasoning}
                  </p>
                </div>

                <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800/50 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-semibold text-slate-100">{localeConfig.analysis.cards.auditor}</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      {currentAnalysis.audit_verification.approved ? (
                        <CheckCircle className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-400" />
                      )}
                      <span className={currentAnalysis.audit_verification.approved ? 'text-emerald-400' : 'text-rose-400'}>
                        {currentAnalysis.audit_verification.approved ? localeConfig.analysis.cards.approved : localeConfig.analysis.cards.rejected}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300">
                      {currentAnalysis.audit_verification.auditor_comments}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'agents' && (
          <div
            id="agents-panel"
            role="tabpanel"
            aria-labelledby="agents-tab"
            className="space-y-6"
          >
            <SectionShell
              id="tri-agent"
              title={localeConfig.agents.title}
              description={localeConfig.agents.description}
            >
              
              <div className="relative">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    {
                      name: localeConfig.agents.analyst.name,
                      role: localeConfig.agents.analyst.role,
                      icon: Activity,
                      color: 'blue',
                      status: systemHealth?.components?.analyst,
                      description: localeConfig.agents.analyst.description,
                      metrics: localeConfig.agents.analyst.metrics
                    },
                    {
                      name: localeConfig.agents.brain.name,
                      role: localeConfig.agents.brain.role,
                      icon: Brain,
                      color: 'purple',
                      status: systemHealth?.components?.jepa,
                      description: localeConfig.agents.brain.description,
                      metrics: [
                        currentAnalysis?.prediction.confidence
                          ? formatters.percent.format(currentAnalysis.prediction.confidence)
                          : localeConfig.agents.brain.metrics[0],
                        localeConfig.agents.brain.metrics[1]
                      ]
                    },
                    {
                      name: localeConfig.agents.strategist.name,
                      role: localeConfig.agents.strategist.role,
                      icon: Zap,
                      color: 'amber',
                      status: systemHealth?.components?.strategist,
                      description: localeConfig.agents.strategist.description,
                      metrics: localeConfig.agents.strategist.metrics
                    }
                  ].map((agent, idx) => (
                    <div key={idx} className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className={`w-12 h-12 rounded-lg bg-${agent.color}-500/10 flex items-center justify-center`}>
                          <agent.icon className={`w-6 h-6 text-${agent.color}-400`} />
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${agent.status === 'healthy' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-500/10 text-slate-400'}`}>
                          {agent.status || 'unknown'}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-slate-100 mb-1">{agent.name}</h3>
                      <p className="text-sm text-slate-400 mb-3">{agent.role}</p>
                      <p className="text-sm text-slate-300 mb-4">{agent.description}</p>
                      <div className="flex gap-2">
                        {agent.metrics.map((metric, i) => (
                          <span key={i} className="text-xs px-2 py-1 bg-slate-900/50 text-slate-400 rounded">
                            {metric}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Connecting arrows */}
                <div className="hidden md:block absolute top-1/2 left-1/3 w-1/6 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 -translate-y-1/2" />
                <div className="hidden md:block absolute top-1/2 right-1/3 w-1/6 h-0.5 bg-gradient-to-r from-purple-500 to-amber-500 -translate-y-1/2" />
              </div>
            </SectionShell>

            {/* Agent Logs */}
            <SectionShell
              id="agent-logs"
              title={localeConfig.logs.title}
              description={localeConfig.logs.description}
              actions={
                <div className="flex items-center gap-2 text-sm">
                  <Filter className="w-4 h-4 text-slate-400" aria-hidden="true" />
                  <select
                    value={logFilter}
                    onChange={(e) => setLogFilter(e.target.value)}
                    className={`bg-slate-900/50 border border-slate-700/60 rounded-lg px-3 py-1 text-slate-200 ${ui.focusRing}`}
                    aria-label={localeConfig.a11y.logsFilter}
                  >
                    <option value="all">{localeConfig.logs.filter.all}</option>
                    <option value="success">{localeConfig.logs.filter.success}</option>
                    <option value="error">{localeConfig.logs.filter.error}</option>
                    <option value="info">{localeConfig.logs.filter.info}</option>
                  </select>
                </div>
              }
            >
              <div className="spacey-2 max-h-96 overflow-y-auto" aria-live="polite">
                {filteredLogs.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">{localeConfig.logs.empty}</p>
                ) : (
                  filteredLogs.map(log => (
                    <div key={log.id} className="flex items-start gap-3 p-3 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-all">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        log.type === 'success' ? 'bg-emerald-400' :
                        log.type === 'error' ? 'bg-rose-400' :
                        'bg-slate-400'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-slate-200">{log.component}</span>
                          <span className="text-xs text-slate-500">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 truncate">{log.message}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </SectionShell>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div
            id="monitoring-panel"
            role="tabpanel"
            aria-labelledby="monitoring-tab"
            className="space-y-6"
          >
            {/* System Health */}
            <SectionShell
              id="system-health"
              title={localeConfig.monitoring.title}
              description={localeConfig.monitoring.description}
            >
              {systemHealth?.components ? (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(systemHealth.components).map(([name, status]) => (
                    <div key={name} className="bg-slate-800/30 rounded-lg p-4 text-center">
                      <div className={`w-8 h-8 mx-auto mb-2 rounded-full ${
                        status === 'healthy' ? 'bg-emerald-500/20' : 'bg-slate-500/20'
                      } flex items-center justify-center`}>
                        {status === 'healthy' ? (
                          <CheckCircle className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-slate-400" />
                        )}
                      </div>
                      <div className="text-sm font-medium text-slate-300 capitalize">{name}</div>
                      <div className={`text-xs mt-1 ${status === 'healthy' ? 'text-emerald-400' : 'text-slate-500'}`}>
                        {status}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Array.from({ length: 5 }).map((_, idx) => (
                    <SkeletonBlock key={idx} className="h-28" label={localeConfig.a11y.skeletons.health} />
                  ))}
                </div>
              )}
            </SectionShell>

            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`${ui.shell} p-6`}>
                <h3 className="text-lg font-bold text-slate-100 mb-4">{localeConfig.monitoring.modelPerformance}</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={[
                    { metric: 'Accuracy', value: 87 },
                    { metric: 'Speed', value: 92 },
                    { metric: 'Reliability', value: 95 },
                    { metric: 'Coverage', value: 78 },
                    { metric: 'Confidence', value: 85 }
                  ]}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8' }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                    <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className={`${ui.shell} p-6`}>
                <h3 className="text-lg font-bold text-slate-100 mb-4">{localeConfig.monitoring.responseTimes}</h3>
                <div className="space-y-3">
                  {[
                    { component: 'Analyst', time: 45, max: 100 },
                    { component: 'JEPA', time: 120, max: 200 },
                    { component: 'Strategist', time: 180, max: 300 },
                    { component: 'Auditor', time: 35, max: 100 }
                  ].map((item, idx) => (
                    <div key={idx}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-300">{item.component}</span>
                        <span className="text-slate-400">{item.time}ms</span>
                      </div>
                      <div className="w-full bg-slate-800/50 rounded-full h-2" aria-hidden="true">
                        <div className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: `${(item.time / item.max) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Prediction Metrics */}
            <SectionShell
              id="prediction-metrics"
              title={localeConfig.monitoring.metrics.title}
              description={localeConfig.monitoring.metrics.description}
              ariaBusy={metricsLoading}
            >
              {metricsError && (
                <div className="mb-4 p-4 rounded-lg border border-rose-500/40 bg-rose-500/10 text-rose-200" role="alert">
                  {metricsError}
                </div>
              )}

              {!metricsError && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.count}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.accuracy?.count ?? '—'}
                    </p>
                  </div>
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.accuracy}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.accuracy?.accuracy !== null && metricsData?.accuracy?.accuracy !== undefined
                        ? `${metricsData.accuracy.accuracy.toFixed(1)}%`
                        : '—'}
                    </p>
                  </div>
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.mae}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.accuracy?.mae !== null && metricsData?.accuracy?.mae !== undefined
                        ? formatters.currency.format(metricsData.accuracy.mae)
                        : '—'}
                    </p>
                  </div>
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.rmse}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.accuracy?.rmse !== null && metricsData?.accuracy?.rmse !== undefined
                        ? formatters.currency.format(metricsData.accuracy.rmse)
                        : '—'}
                    </p>
                  </div>
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.epochs}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.training?.epochs ?? '—'}
                    </p>
                  </div>
                  <div className={`${ui.surface} p-4`}>
                    <p className={`text-xs ${ui.textMuted}`}>{localeConfig.monitoring.metrics.fields.currentLoss}</p>
                    <p className="text-2xl font-semibold">
                      {metricsData?.training?.current_loss !== null && metricsData?.training?.current_loss !== undefined
                        ? metricsData.training.current_loss.toFixed(4)
                        : '—'}
                    </p>
                    {metricsData?.training?.improvement !== null && metricsData?.training?.improvement !== undefined && (
                      <p className="text-xs text-emerald-400">
                        {localeConfig.monitoring.metrics.fields.improvement}: {metricsData.training.improvement.toFixed(1)}%
                      </p>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-8">
                <h4 className="text-sm font-semibold text-slate-300 mb-2">{localeConfig.monitoring.metrics.recentTitle}</h4>
                <p className={`text-xs mb-4 ${ui.textMuted}`}>{localeConfig.monitoring.metrics.recentDescription}</p>
                {metricsLoading ? (
                  <SkeletonBlock className="h-40" label={localeConfig.a11y.skeletons.chart} />
                ) : metricsData?.recent_predictions?.length ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead className="text-slate-400">
                        <tr>
                          <th className="text-left py-2">{localeConfig.overview.quickAnalysis.fields.liquidity}</th>
                          <th className="text-left py-2">{localeConfig.overview.quickAnalysis.fields.riskScore}</th>
                          <th className="text-left py-2">{localeConfig.monitoring.metrics.fields.accuracy}</th>
                          <th className="text-left py-2">{localeConfig.header.localeLabel}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {metricsData.recent_predictions.map((prediction, idx) => (
                          <tr key={idx} className="border-t border-slate-800/50">
                            <td className="py-2 text-slate-200">
                              {formatters.currencyCompact.format(prediction.predicted)}
                            </td>
                            <td className="py-2 text-slate-200">
                              {prediction.actual ? formatters.currencyCompact.format(prediction.actual) : '—'}
                            </td>
                            <td className="py-2 text-slate-200">
                              {prediction.actual
                                ? `${(100 - Math.abs(prediction.predicted - prediction.actual) / prediction.actual * 100).toFixed(1)}%`
                                : '—'}
                            </td>
                            <td className="py-2 text-slate-400">
                              {formatters.time(prediction.timestamp)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className={`text-slate-400 text-center py-6`}>{localeConfig.monitoring.metrics.empty}</p>
                )}
              </div>
            </SectionShell>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 bg-slate-950/50 backdrop-blur-xl mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-slate-400">
            <div>
              {localeConfig.footer.summary}
            </div>
            <div className="flex items-center gap-4">
              <span>{localeConfig.footer.modePrefix} {systemHealth?.mode || localeConfig.header.mode.mock}</span>
              <span>•</span>
              <span>{localeConfig.footer.uptime}</span>
              <span>•</span>
              <span>{localeConfig.footer.compliance}</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SenseForgeDashboard;
