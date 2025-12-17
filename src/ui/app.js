function appState() {
  return {
    urlsInput: '',
    runId: null,
    sse: null,
    statusText: 'מוכן',
    mockOutbound: true,
    loading: false,
    logs: [],
    metrics: { scanned: 0, passed: 0, failed: 0 },
    regions: { 'מרכז': [], 'צפון': [], 'דרום': [], 'ירושלים': [], 'אחר': [] },

    init() {
      this.fetchSources();
    },

    resetState() {
      this.metrics = { scanned: 0, passed: 0, failed: 0 };
      this.logs = [];
      this.regions = { 'מרכז': [], 'צפון': [], 'דרום': [], 'ירושלים': [], 'אחר': [] };
    },

    async fetchSources() {
      try {
        const resp = await fetch('/sources/suggest');
        if (!resp.ok) return;
        const data = await resp.json();
        if (data.urls?.length) {
          const existing = this.urlsInput ? this.urlsInput.split(/\n+/).filter(Boolean) : [];
          const merged = Array.from(new Set([...data.urls, ...existing]));
          this.urlsInput = merged.join('\n');
        }
      } catch (err) {
        console.error('sources fetch failed', err);
      }
    },

    async startRun() {
      const urls = this.urlsInput.split(/\n+/).map(u => u.trim()).filter(Boolean);
      if (!urls.length) {
        alert('אנא הזן לפחות מקור אחד');
        return;
      }
      this.loading = true;
      this.resetState();
      try {
        const resp = await fetch('/runs/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ raw_urls: this.urlsInput, urls, use_mock_outbound: this.mockOutbound }),
        });
        const data = await resp.json();
        this.runId = data.run_id;
        this.statusText = `ריצה ${this.runId}`;
        this.startSSE(this.runId);
      } catch (err) {
        console.error('failed to start run', err);
        alert('שגיאה בהפעלת הריצה');
      } finally {
        this.loading = false;
      }
    },

    async stopRun() {
      if (!this.runId) return;
      await fetch('/runs/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ run_id: this.runId })
      });
      this.statusText = 'הריצה נעצרה';
    },

    startSSE(runId) {
      if (this.sse) {
        this.sse.close();
      }
      this.sse = new EventSource('/events/stream');
      this.sse.onmessage = (ev) => {
        const payload = JSON.parse(ev.data);
        this.handleEvent(payload);
      };
      this.sse.onerror = () => {
        this.addLog('חיבור SSE נותק', 'error');
      };
    },

    handleEvent(payload) {
      if (!payload || payload.run_id !== this.runId) return;
      const eventType = payload.event_type;
      const message = payload.message || '';
      const eventKey = payload.data?.event;

      this.statusText = message;
      this.addLog(message, eventType);

      if (eventKey === 'job_passed') {
        this.metrics.scanned += 1;
        this.metrics.passed += 1;
        if (payload.data?.job) this.addJob(payload.data.job);
      } else if (eventKey === 'job_skipped') {
        this.metrics.scanned += 1;
        this.metrics.failed += 1;
      } else if (eventKey === 'outbound_saved') {
        this.markOutboundSaved(payload.data?.job_url);
      }
    },

    addJob(job) {
      const region = job.region || 'אחר';
      if (!this.regions[region]) this.regions[region] = [];
      const score = job.filter?.score ?? job.score ?? job.classification?.score ?? '';
      const entry = {
        url: job.url,
        title: job.title || job.url,
        company: job.company || '',
        location: job.location || '',
        summary: job.summary || '',
        score: score ? Number(score).toFixed(2) : '',
        outboundSaved: false,
      };
      this.regions[region].unshift(entry);
    },

    markOutboundSaved(jobUrl) {
      if (!jobUrl) return;
      Object.keys(this.regions).forEach(region => {
        this.regions[region] = this.regions[region].map(job =>
          job.url === jobUrl ? { ...job, outboundSaved: true } : job
        );
      });
    },

    addLog(message, type = 'info') {
      const ts = new Date().toLocaleTimeString('he-IL', { hour12: false });
      this.logs.unshift({ id: `${Date.now()}-${Math.random()}`, message, type, time: ts });
      if (this.logs.length > 200) this.logs.pop();
    },
  };
}

window.appState = appState;
