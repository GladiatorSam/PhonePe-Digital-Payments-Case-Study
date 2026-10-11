"""Build the two small CSV extracts used by the notebook from the full Our World in Data (OWID) file.

Usage:
    python src/make_extract.py            # downloads the OWID file, writes data/*.csv
    python src/make_extract.py path.csv   # uses a local copy of owid-covid-data.csv
"""
import sys
import pandas as pd

URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
SELECTED = ["India", "United States", "Brazil", "United Kingdom", "Germany",
            "Japan", "South Africa", "Russia", "Indonesia", "Italy"]
DAILY_COLS = ["iso_code", "continent", "location", "date", "total_cases", "new_cases",
              "new_cases_smoothed", "total_deaths", "new_deaths", "new_deaths_smoothed",
              "total_cases_per_million", "total_deaths_per_million",
              "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred",
              "stringency_index", "population"]
SNAP_STATIC = ["iso_code", "continent", "population", "median_age", "aged_65_older",
               "gdp_per_capita", "human_development_index"]
SNAP_LAST = ["total_cases", "total_deaths", "total_cases_per_million", "total_deaths_per_million"]
SNAP_MAX = ["people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred"]


def main(src=URL):
    df = pd.read_csv(src, parse_dates=["date"], low_memory=False)
    # Keep real countries only: OWID adds aggregates such as 'World' and 'Asia' with iso codes starting 'OWID_'
    countries = df[~df["iso_code"].str.startswith("OWID_", na=False) & df["continent"].notna()]

    daily = countries[countries["location"].isin(SELECTED)][DAILY_COLS]
    daily.to_csv("data/covid_selected_countries_daily.csv", index=False)

    g = countries.sort_values("date").groupby("location")
    snap = g[SNAP_STATIC + SNAP_LAST].last()                      # last non-missing value per country
    snap["max_people_vaccinated_per_hundred"] = g[SNAP_MAX[0]].max()
    snap["max_fully_vaccinated_per_hundred"] = g[SNAP_MAX[1]].max()
    snap["last_case_report_date"] = countries.dropna(subset=["total_cases"]).groupby("location")["date"].max()
    snap.reset_index().to_csv("data/covid_country_snapshot.csv", index=False)
    print("daily rows:", len(daily), "| countries in snapshot:", len(snap))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else URL)
