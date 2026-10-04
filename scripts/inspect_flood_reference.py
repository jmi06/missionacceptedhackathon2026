from __future__ import annotations

import json
from pathlib import Path
import sqlite3


PATH = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon\data\reference\historical_flood_event_en.gpkg")


with sqlite3.connect(PATH) as connection:
    contents = connection.execute(
        "SELECT table_name, data_type, identifier, description, min_x, min_y, max_x, max_y, srs_id FROM gpkg_contents"
    ).fetchall()
    report = {"contents": []}
    for row in contents:
        table = row[0]
        columns = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
        count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        samples = connection.execute(f'SELECT * FROM "{table}" LIMIT 3').fetchall()
        report["contents"].append({
            "table": table,
            "data_type": row[1],
            "identifier": row[2],
            "description": row[3],
            "extent": row[4:8],
            "srs_id": row[8],
            "record_count": count,
            "columns": [{"index": c[0], "name": c[1], "type": c[2]} for c in columns],
            "sample_rows_without_geometry": [
                {columns[i][1]: value for i, value in enumerate(sample) if columns[i][1].lower() not in {"geom", "geometry"}}
                for sample in samples
            ],
        })
    metadata_tables = [
        name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if "metadata" in name.lower()
    ]
    report["metadata_tables"] = metadata_tables
    for table in metadata_tables:
        try:
            report[table] = connection.execute(f'SELECT * FROM "{table}" LIMIT 20').fetchall()
        except sqlite3.DatabaseError:
            pass
    print(json.dumps(report, indent=2, default=str))
