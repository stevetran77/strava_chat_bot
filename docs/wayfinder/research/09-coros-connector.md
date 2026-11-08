# Research 09: COROS connector data and limits

Method: read-only calls made from the main Claude Code session on 2026-11-08, plus two web lookups. No write tools were called. No personal values are recorded below.

## What the connector is

- Hosted at `mcpus.coros.com`, installed as the claude.ai connector "claude.ai COROS" (from the tool description). Needs OAuth login through `/mcp`.
- Web search found no official COROS documentation for this connector. [UNVERIFIED] whether it is official, its cost, and its terms.

## Tool inventory (names from the session)

- Read, activity: `querySportRecords`, `getActivityDetail`, `queryActivityLapData`, `queryCustomActivityLapData`, `downloadActivityFitFiles`, `queryActivityFitFileDownloadUrls`.
- Read, health: `queryDailyHealthData`, `querySleepOverview`, `querySleepHrv`, `queryRestingHeartRate`, `queryAvgHeartRate`, `queryStressLevel`, `queryStressTimeSeries`, `queryHealthCheckTimeSeries`, `queryRecoveryStatus`, `queryMenstruationCycles`.
- Read, training: `queryTrainingLoadAssessment`, `queryFitnessAssessmentOverview`, `queryTrainingSchedule`, `queryTrainingPlanDetails`, `queryTrainingPlanLibrary`, `queryWorkoutDetails`, `queryWorkoutLibrary`, `queryScheduledWorkoutDetails`, `queryUserInfo`, `queryDevices`.
- Write (not used, out of scope): `createScheduledWorkout`, `createSingleWorkout`, `createTrainingPlan`, `scheduleWorkout`, `updateScheduledWorkout`, `updateTrainingPlan`, `updateWorkoutDetails`, `uploadRouteFile`.

## Data shape observed

- `querySportRecords`: filters by date range, sport type codes, distance, duration, pace, location; `limit` default 20.
  - Per record: date, sport name, location label, start coordinates, start/end timestamps, duration, distance, average pace (or speed), average HR, calories, `labelId`, `sportType`.
  - Output is a human-readable text block, not JSON. Ingestion needs text parsing.
- `getActivityDetail`: text block with workout time, distance, average/moving/adjusted pace, best km, average HR, cadence, stride length, power, elevation gain/loss, calories, Training Load, Aerobic and Anaerobic TE, Training Focus, Performance. Text, not JSON.
- `queryActivityLapData`: JSON. Column list of about 25 fields (pace, power, HR, max HR, ground time, cadence, stride metrics, elevation, adjusted pace, and more), column labels in Chinese. Lap groups for 1 km laps, 5 km laps, and whole activity. Some fields are 0 when the sensor does not provide them. Distances appear in units of 1/100,000 km scale (1 km shown as 100000) [UNVERIFIED unit].
- Daily health: text with resting HR, HRV baseline, steps, calories, exercise minutes, stress average. Sleep score returned 0 and "not available yet" for the two most recent days.
- Training load: text with daily comment, short-term load, long-term load, load ratio.
- Also available per tool descriptions (not called): fitness assessment (VO2max, threshold pace, race predictions), recovery status.

## History depth and volume

- One query with limit 200 returned 66,370 characters, over the output limit, so it was saved to a file. Large pulls must be chunked by date range.
- Records exist at least back to 2023-12-31. Earliest record not located [UNVERIFIED]. About 200 records fall between 2025-09-05 and 2026-11-07.
- Sports seen in the 200 most recent records: outdoor run (117), walk, open water swim, cycling, trail run, floor climb, strength, indoor run.

## Limits and unknowns

- FIT file tools mention a daily FIT file limit, number not stated; URL fetch returns max 10 per call (default 5).
- `queryDevices` returned "No devices found" while activities exist. Cause unknown [UNVERIFIED].
- Rate limits, cost, and data-storage terms: not found.
- Start coordinates are returned for every activity (private data).

## Can the local chatbot call it directly?

- Not established [UNVERIFIED]. The connector is exposed through a claude.ai proxy and authenticated through the Claude session. No evidence either way that an outside client can use it.
- Safe assumption: data reaches the local store only through a Claude session.

## Alternative path found (unofficial)

- `coros-cli` / "splitlog" ([github.com/simon-hv/coros-cli](https://github.com/simon-hv/coros-cli)): unofficial CLI and local MCP server for COROS Training Hub.
  - Says it is not affiliated with or endorsed by COROS, warns APIs may change, and discusses neither terms of service nor rate limits.
  - Login stores an MD5 hash of the password in `~/.config/splitlog/config.json` and re-logs in with it. Treat as a security risk before considering use.
  - Exports activities with laps and zones, plus health data. FIT files not mentioned.

## Sources

- Tool descriptions and outputs from the claude.ai COROS connector in this session.
- Web search results (no official COROS source found); GitHub page above (read through a summarizing fetch).
