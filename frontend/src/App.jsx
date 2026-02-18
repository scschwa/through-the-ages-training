import { useState, useCallback, useEffect, useRef } from 'react'
import { marked } from 'marked'

// ── Example game states (mirrors the JSON files in data/) ──────────────────

const EXAMPLES = {
  '': null,
  'Age I — Needs 5th CA': {
    age: 1, round: 3, player_count: 4,
    civil_actions: 4, military_actions: 2,
    food_production: 5, ore_production: 3,
    science_production: 1, culture_production: 2,
    military_strength: 5, culture_points: 4,
    leader: 'Moses', wonders_complete: '', wonders_in_progress: '',
    technologies: 'Bronze Age', hand_cards: '',
    opp1_mil: 7, opp1_cult_prod: 2, opp1_cult_pts: 5,
    opp2_mil: 6, opp2_cult_prod: 3, opp2_cult_pts: 6,
    opp3_mil: 4, opp3_cult_prod: 2, opp3_cult_pts: 3,
    card_row: 'Code of Laws, Swordsmen, Library, Irrigation',
    next_event: 'Age of Expansion',
  },
  'Age II — Military Crisis (Shakespeare)': {
    age: 2, round: 2, player_count: 4,
    civil_actions: 5, military_actions: 3,
    food_production: 9, ore_production: 7,
    science_production: 5, culture_production: 8,
    military_strength: 10, culture_points: 28,
    leader: 'Shakespeare', wonders_complete: 'Pyramids', wonders_in_progress: '',
    technologies: 'Chivalry, Printing Press, Philosophy', hand_cards: 'Drama',
    opp1_mil: 16, opp1_cult_prod: 5, opp1_cult_pts: 22,
    opp2_mil: 12, opp2_cult_prod: 6, opp2_cult_pts: 25,
    opp3_mil: 11, opp3_cult_prod: 4, opp3_cult_pts: 18,
    card_row: 'Knights, Tactics, Code of Laws, Alchemy',
    next_event: 'Military Dominance',
  },
  'Age II — Balanced Mid-Game': {
    age: 2, round: 4, player_count: 4,
    civil_actions: 5, military_actions: 3,
    food_production: 8, ore_production: 6,
    science_production: 4, culture_production: 7,
    military_strength: 12, culture_points: 34,
    leader: 'Caesar', wonders_complete: 'Hanging Gardens', wonders_in_progress: '',
    technologies: 'Chivalry, Printing Press', hand_cards: 'Code of Laws, Drama',
    opp1_mil: 14, opp1_cult_prod: 5, opp1_cult_pts: 28,
    opp2_mil: 11, opp2_cult_prod: 7, opp2_cult_pts: 32,
    opp3_mil: 13, opp3_cult_prod: 4, opp3_cult_pts: 20,
    card_row: 'Philosophy, Tactics, Aqueduct, Shakespeare',
    next_event: 'Exploration',
  },
}

// ── Initial form state ─────────────────────────────────────────────────────

const DEFAULT_FORM = {
  age: 1, round: 1, player_count: 4,
  civil_actions: 5, military_actions: 3,
  food_production: 5, ore_production: 4,
  science_production: 2, culture_production: 2,
  military_strength: 6, culture_points: 5,
  leader: '', wonders_complete: '', wonders_in_progress: '',
  technologies: '', hand_cards: '',
  opp1_mil: 6, opp1_cult_prod: 2, opp1_cult_pts: 5,
  opp2_mil: 6, opp2_cult_prod: 2, opp2_cult_pts: 5,
  opp3_mil: 6, opp3_cult_prod: 2, opp3_cult_pts: 5,
  card_row: '',
  next_event: '',
}

// ── Image resizing ─────────────────────────────────────────────────────────

/**
 * Resize + compress an image data URL to stay under Anthropic's 5MB limit.
 * Returns a JPEG data URL at the given max width and quality.
 */
const resizeImage = (dataUrl, maxWidth = 1920, quality = 0.82) =>
  new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      let { width, height } = img
      if (width > maxWidth) {
        height = Math.round(height * maxWidth / width)
        width = maxWidth
      }
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      canvas.getContext('2d').drawImage(img, 0, 0, width, height)
      resolve(canvas.toDataURL('image/jpeg', quality))
    }
    img.src = dataUrl
  })

// ── Helpers ────────────────────────────────────────────────────────────────

const parseList = (text) =>
  text ? text.split(',').map(s => s.trim()).filter(Boolean) : []

/** Convert flat form state → nested API request body */
const toApiGameState = (f) => ({
  meta: { age: f.age, round: f.round, player_count: f.player_count },
  player: {
    civil_actions: f.civil_actions,
    military_actions: f.military_actions,
    food_production: f.food_production,
    ore_production: f.ore_production,
    science_production: f.science_production,
    culture_production: f.culture_production,
    military_strength: f.military_strength,
    culture_points: f.culture_points,
    leader: f.leader || null,
    wonders_complete: parseList(f.wonders_complete),
    wonders_in_progress: parseList(f.wonders_in_progress),
    technologies: parseList(f.technologies),
    hand_cards: parseList(f.hand_cards),
  },
  opponents: [
    { id: 'opp1', military_strength: f.opp1_mil, culture_production_estimate: f.opp1_cult_prod, culture_points_estimate: f.opp1_cult_pts },
    { id: 'opp2', military_strength: f.opp2_mil, culture_production_estimate: f.opp2_cult_prod, culture_points_estimate: f.opp2_cult_pts },
    { id: 'opp3', military_strength: f.opp3_mil, culture_production_estimate: f.opp3_cult_prod, culture_points_estimate: f.opp3_cult_pts },
  ].filter(o => o.military_strength > 0),
  card_row: {
    age_1_cards: f.age === 1 ? parseList(f.card_row) : [],
    age_2_cards: f.age === 2 ? parseList(f.card_row) : [],
    age_3_cards: f.age === 3 ? parseList(f.card_row) : [],
  },
  events: { next_visible: f.next_event || null },
})

/** Compute live military status for the UI warning banner */
const getMilStatus = (form) => {
  const myMil = form.military_strength
  const oppMax = Math.max(form.opp1_mil, form.opp2_mil, form.opp3_mil)
  const gap = oppMax - myMil
  if (gap > 4) return { cls: 'mil-warning', msg: `!! Military gap of ${gap} — urgent, well above safe threshold of 2` }
  if (gap > 2) return { cls: 'mil-caution', msg: `Military gap of ${gap} — above threshold, address soon` }
  if (gap > 0) return { cls: 'mil-ok', msg: `Military gap of ${gap} — within safe threshold (≤2)` }
  if (gap === 0) return { cls: 'mil-lead', msg: `Military tied with strongest opponent` }
  return { cls: 'mil-lead', msg: `Military leading by ${-gap} — no immediate threat` }
}

// ── Component ──────────────────────────────────────────────────────────────

export default function App() {
  const [form, setForm] = useState(DEFAULT_FORM)
  const [proposedMove, setProposedMove] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [lastAction, setLastAction] = useState('')

  // Screenshot state
  const [screenshot, setScreenshot] = useState(null)   // data URL for preview
  const [parsing, setParsing] = useState(false)
  const [parseNotes, setParseNotes] = useState('')
  const [parseError, setParseError] = useState('')
  const fileInputRef = useRef(null)

  const set = useCallback((key, value) =>
    setForm(prev => ({ ...prev, [key]: value })), [])

  const setNum = useCallback((key, value) =>
    setForm(prev => ({ ...prev, [key]: parseInt(value) || 0 })), [])

  const loadExample = (name) => {
    const ex = EXAMPLES[name]
    if (ex) setForm({ ...DEFAULT_FORM, ...ex })
  }

  const callApi = async (endpoint, body) => {
    setLoading(true)
    setError('')
    setResponse('')
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      setResponse(data.advice)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSuggest = () => {
    setLastAction('suggest')
    callApi('/api/suggest-moves', { game_state: toApiGameState(form) })
  }

  const handleEvaluate = () => {
    if (!proposedMove.trim()) return
    setLastAction('evaluate')
    callApi('/api/evaluate-move', {
      game_state: toApiGameState(form),
      proposed_move: proposedMove.trim(),
    })
  }

  // ── Screenshot parsing ───────────────────────────────────────────────────

  const populateFormFromGameState = useCallback((gs) => {
    const p = gs.player || {}
    const opps = gs.opponents || []
    const cr = gs.card_row || {}
    const allCards = [
      ...(cr.age_1_cards || []),
      ...(cr.age_2_cards || []),
      ...(cr.age_3_cards || []),
    ]
    setForm(prev => ({
      ...prev,
      age:    gs.meta?.age    ?? prev.age,
      round:  gs.meta?.round  ?? prev.round,
      player_count: gs.meta?.player_count ?? prev.player_count,
      civil_actions:    p.civil_actions    ?? prev.civil_actions,
      military_actions: p.military_actions ?? prev.military_actions,
      food_production:  p.food_production  ?? prev.food_production,
      ore_production:   p.ore_production   ?? prev.ore_production,
      science_production: p.science_production ?? prev.science_production,
      culture_production: p.culture_production ?? prev.culture_production,
      military_strength: p.military_strength  ?? prev.military_strength,
      culture_points:    p.culture_points     ?? prev.culture_points,
      leader:            p.leader || '',
      wonders_complete:  (p.wonders_complete  || []).join(', '),
      wonders_in_progress: (p.wonders_in_progress || []).join(', '),
      technologies:      (p.technologies || []).join(', '),
      hand_cards:        (p.hand_cards   || []).join(', '),
      opp1_mil:       opps[0]?.military_strength          ?? prev.opp1_mil,
      opp1_cult_prod: opps[0]?.culture_production_estimate ?? prev.opp1_cult_prod,
      opp1_cult_pts:  opps[0]?.culture_points_estimate     ?? prev.opp1_cult_pts,
      opp2_mil:       opps[1]?.military_strength          ?? prev.opp2_mil,
      opp2_cult_prod: opps[1]?.culture_production_estimate ?? prev.opp2_cult_prod,
      opp2_cult_pts:  opps[1]?.culture_points_estimate     ?? prev.opp2_cult_pts,
      opp3_mil:       opps[2]?.military_strength          ?? prev.opp3_mil,
      opp3_cult_prod: opps[2]?.culture_production_estimate ?? prev.opp3_cult_prod,
      opp3_cult_pts:  opps[2]?.culture_points_estimate     ?? prev.opp3_cult_pts,
      card_row:   allCards.join(', '),
      next_event: gs.events?.next_visible || '',
    }))
  }, [])

  const parseScreenshotData = useCallback(async (dataUrl) => {
    setParsing(true)
    setParseNotes('')
    setParseError('')
    const [, base64] = dataUrl.split(',')
    const mediaType = 'image/jpeg'   // resizeImage always produces JPEG
    try {
      const res = await fetch('/api/parse-screenshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64, media_type: mediaType }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      populateFormFromGameState(data.game_state)
      setParseNotes(data.notes || 'Game state loaded from screenshot.')
    } catch (e) {
      setParseError(e.message)
    } finally {
      setParsing(false)
    }
  }, [populateFormFromGameState])

  const handleImageData = useCallback(async (dataUrl) => {
    setScreenshot(dataUrl)              // show original as preview immediately
    const compressed = await resizeImage(dataUrl)  // resize before sending to API
    parseScreenshotData(compressed)
  }, [parseScreenshotData])

  // Ctrl+V paste anywhere on the page
  useEffect(() => {
    const onPaste = (e) => {
      const items = e.clipboardData?.items
      if (!items) return
      for (const item of items) {
        if (item.type.startsWith('image/')) {
          const blob = item.getAsFile()
          const reader = new FileReader()
          reader.onload = (ev) => handleImageData(ev.target.result)
          reader.readAsDataURL(blob)
          break
        }
      }
    }
    window.addEventListener('paste', onPaste)
    return () => window.removeEventListener('paste', onPaste)
  }, [handleImageData])

  const handleFileInput = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => handleImageData(ev.target.result)
    reader.readAsDataURL(file)
    e.target.value = ''   // reset so same file can be re-selected
  }

  const milStatus = getMilStatus(form)

  // Number input helper
  const NumInput = ({ label, field, min = 0 }) => (
    <div className="field">
      <label>{label}</label>
      <input
        type="number"
        min={min}
        value={form[field]}
        onChange={e => setNum(field, e.target.value)}
      />
    </div>
  )

  const TextInput = ({ label, field, placeholder = '' }) => (
    <div className="field span2">
      <label>{label}</label>
      <input
        type="text"
        value={form[field]}
        placeholder={placeholder}
        onChange={e => set(field, e.target.value)}
      />
    </div>
  )

  return (
    <div className="app">
      <header className="app-header">
        <h1>Through the Ages — <span>AI Coach</span></h1>
        <span className="model-badge">claude-sonnet-4-6</span>
      </header>

      <div className="app-body">

        {/* ── Left Panel: Game State Form ─────────────────────────── */}
        <div className="form-panel">

          {/* Screenshot Parser */}
          <div className="card">
            <div className="card-title">Parse Screenshot</div>
            <div className="screenshot-drop" onClick={() => fileInputRef.current?.click()}>
              {screenshot ? (
                <img src={screenshot} alt="Game screenshot" className="screenshot-preview" />
              ) : (
                <div className="screenshot-hint">
                  <span className="screenshot-icon">📷</span>
                  <span>Paste a screenshot (<kbd>Ctrl+V</kbd>) or click to upload</span>
                  <span className="screenshot-sub">Claude will read your board and fill in the form</span>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileInput}
            />
            {parsing && (
              <div className="loading-row" style={{ marginTop: '0.5rem' }}>
                <div className="spinner" />
                <span>Analyzing screenshot...</span>
              </div>
            )}
            {parseNotes && !parsing && (
              <div className="parse-notes">✓ {parseNotes}</div>
            )}
            {parseError && !parsing && (
              <div className="error-box" style={{ marginTop: '0.5rem' }}>{parseError}</div>
            )}
          </div>

          {/* Load Example */}
          <div className="card">
            <div className="example-row">
              <label>Or load example:</label>
              <select onChange={e => loadExample(e.target.value)} defaultValue="">
                {Object.keys(EXAMPLES).map(name => (
                  <option key={name} value={name}>{name || '— select —'}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Situation */}
          <div className="card">
            <div className="card-title">Situation</div>
            <div className="field" style={{ marginBottom: '0.5rem' }}>
              <label>Age</label>
              <div className="age-selector">
                {[1, 2, 3].map(a => (
                  <button
                    key={a}
                    className={`age-btn${form.age === a ? ' active' : ''}`}
                    onClick={() => set('age', a)}
                  >
                    Age {a}
                  </button>
                ))}
              </div>
            </div>
            <div className="field-grid">
              <div className="field">
                <label>Round</label>
                <input type="number" min={1} value={form.round}
                  onChange={e => setNum('round', e.target.value)} />
              </div>
              <div className="field">
                <label>Player Count</label>
                <input type="number" min={2} max={4} value={form.player_count}
                  onChange={e => setNum('player_count', e.target.value)} />
              </div>
            </div>
          </div>

          {/* Your Civilization */}
          <div className="card">
            <div className="card-title">Your Civilization</div>
            <div className="field-grid">
              <NumInput label="Civil Actions" field="civil_actions" />
              <NumInput label="Military Actions" field="military_actions" />
              <NumInput label="Food / turn" field="food_production" />
              <NumInput label="Ore / turn" field="ore_production" />
              <NumInput label="Science / turn" field="science_production" />
              <NumInput label="Culture / turn" field="culture_production" />
              <NumInput label="Military Strength" field="military_strength" />
              <NumInput label="Culture Points" field="culture_points" />
              <TextInput label="Leader" field="leader" placeholder="e.g. Shakespeare" />
              <TextInput label="Hand Cards (comma-separated)" field="hand_cards" placeholder="e.g. Drama, Knights" />
              <TextInput label="Technologies Built (comma-separated)" field="technologies" placeholder="e.g. Chivalry, Printing Press" />
              <TextInput label="Wonders Complete" field="wonders_complete" placeholder="e.g. Pyramids" />
              <TextInput label="Wonders In Progress" field="wonders_in_progress" placeholder="e.g. Hanging Gardens" />
            </div>
          </div>

          {/* Opponents */}
          <div className="card">
            <div className="card-title">Opponents</div>
            <div className="opponent-row" style={{ marginBottom: '0.2rem' }}>
              <div />
              <div className="field"><label>Military</label></div>
              <div className="field"><label>Cult/turn</label></div>
              <div className="field"><label>Cult Pts</label></div>
            </div>
            {[1, 2, 3].map(i => (
              <div className="opponent-row" key={i}>
                <div className="opp-label">Opp {i}</div>
                <div className="field">
                  <input type="number" min={0} value={form[`opp${i}_mil`]}
                    onChange={e => setNum(`opp${i}_mil`, e.target.value)} />
                </div>
                <div className="field">
                  <input type="number" min={0} value={form[`opp${i}_cult_prod`]}
                    onChange={e => setNum(`opp${i}_cult_prod`, e.target.value)} />
                </div>
                <div className="field">
                  <input type="number" min={0} value={form[`opp${i}_cult_pts`]}
                    onChange={e => setNum(`opp${i}_cult_pts`, e.target.value)} />
                </div>
              </div>
            ))}
            <div className={`mil-status ${milStatus.cls}`}>{milStatus.msg}</div>
          </div>

          {/* Context */}
          <div className="card">
            <div className="card-title">Context</div>
            <div className="field-grid">
              <TextInput label="Cards in Row (comma-separated)" field="card_row" placeholder="e.g. Knights, Tactics, Drama" />
              <TextInput label="Next Visible Event" field="next_event" placeholder="e.g. Military Dominance" />
            </div>
          </div>

        </div>

        {/* ── Right Panel: Coaching ───────────────────────────────── */}
        <div className="coaching-panel">

          {/* Suggest Moves */}
          <div className="card">
            <div className="card-title">What should I do this turn?</div>
            <button
              className="btn btn-primary"
              onClick={handleSuggest}
              disabled={loading}
            >
              {loading && lastAction === 'suggest' ? 'Thinking...' : 'Suggest Top 3 Moves'}
            </button>
          </div>

          {/* Evaluate a Move */}
          <div className="card">
            <div className="card-title">Evaluate a specific move</div>
            <textarea
              className="move-textarea"
              placeholder='Describe the move you are considering, e.g. "Draft Code of Laws from the card row"'
              value={proposedMove}
              onChange={e => setProposedMove(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) handleEvaluate() }}
            />
            <div style={{ marginTop: '0.5rem' }}>
              <button
                className="btn btn-danger"
                onClick={handleEvaluate}
                disabled={loading || !proposedMove.trim()}
              >
                {loading && lastAction === 'evaluate' ? 'Thinking...' : 'Evaluate This Move'}
              </button>
            </div>
          </div>

          {/* Response */}
          <div className="card" style={{ flex: 1 }}>
            <div className="card-title">Coach Response</div>

            {loading && (
              <div className="loading-row">
                <div className="spinner" />
                <span>Consulting strategy knowledge base...</span>
              </div>
            )}

            {error && !loading && (
              <div className="error-box">
                <strong>Error:</strong> {error}
              </div>
            )}

            {!loading && !error && !response && (
              <div className="response-placeholder">
                Enter your game state and click a button above to get coaching advice.
              </div>
            )}

            {!loading && !error && response && (
              <div
                className="response-content"
                // Content comes from Claude API, not user input — XSS risk is minimal
                dangerouslySetInnerHTML={{ __html: marked(response) }}
              />
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
