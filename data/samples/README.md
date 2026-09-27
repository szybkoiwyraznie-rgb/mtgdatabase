# Sample scenarios (v2)

Active product data for the new flow.

- `scenarios.jsonl` — hand-written small-batch sample scenarios. One JSON object
  per story. Each scenario describes one short homogeneous sound sample, not a
  multi-layer scene.
- `generated-manifest.jsonl` — appended by the ElevenLabs scout when MP3s are
  generated.

Required scenario fields:

```json
{"story_id":"1","title":"Dunland Crebain","sample_scenario":"ostre krakanie kruka pikującego nad skalnym wąwozem","prompt":"A single sharp raven caw diving over a rocky ravine, dark and close, 2 seconds, no music, no speech.","duration_seconds":2.5,"status":"ready","batch":"b001"}
```
