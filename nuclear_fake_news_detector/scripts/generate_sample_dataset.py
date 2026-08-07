"""
Generates data/sample_dataset.csv — an EXPANDED, UK & IAEA focused starter
dataset of nuclear-power-safety statements labeled real (1) / fake (0).

Includes data sources specific to nuclear fact-checking:
- IAEA Incident and Emergency Centre reports
- National regulators (UK Office for Nuclear Regulation - ONR, US NRC)
- Radiation monitoring networks (EURDEP, EPA RadNet)
- Nuclear fact-checking archives (Full Fact UK, Snopes, PolitiFact)

Run:  python scripts/generate_sample_dataset.py
"""
import csv
import random
import os

random.seed(42)

# UK Nuclear Power Stations and IAEA international reference sites
PLANTS = [
    "Hinkley Point C", "Sizewell B", "Torness", "Heysham 1", "Heysham 2",
    "Dungeness B", "Hunterston B", "Wylfa", "Oldbury", "Sellafield",
    "Springfields", "Capenhurst", "Hartlepool", "Bradwell", "Sizewell C",
    "Fukushima Daiichi", "Chernobyl", "Zaporizhzhia"
]

AGENCIES = [
    "the IAEA Incident and Emergency Centre", "the IAEA",
    "the UK Office for Nuclear Regulation (ONR)", "the UK Atomic Energy Authority (UKAEA)",
    "the Department for Energy Security and Net Zero (DESNZ)", "EDF Energy",
    "the World Nuclear Association", "independent ONR inspectors",
    "the EURDEP radiation monitoring network", "Full Fact UK",
    "the Nuclear Regulatory Commission (NRC)"
]

NUMBERS = ["0.01", "0.02", "0.05", "0.1", "0.3", "1.2", "2.5"]
UNITS = ["millisieverts", "microsieverts per hour", "becquerels per litre"]
DATES = [
    "this week", "on 04/08/2026", "in a report dated 15/07/2026",
    "following routine review on 01/08/2026", "after a scheduled inspection on 22/06/2026",
    "in the latest quarterly update (04/08/2026)", "in an official IAEA IEC bulletin"
]

REAL_TEMPLATES = [
    "{plant} completed a scheduled safety inspection {date} with no radiological anomalies reported.",
    "{agency} confirmed that {plant} remains within all licensed safety limits following routine monitoring.",
    "Independent radiation monitoring around {plant} via EURDEP shows levels of {num} {unit}, consistent with natural background radiation.",
    "The operator of {plant} published its annual environmental safety report {date}, confirming compliance with ONR regulatory standards.",
    "{plant}'s containment systems passed a stress test as part of periodic safety review requirements.",
    "{agency} stated that a minor water leak at {plant} was contained within safety protocols and posed no risk to public health.",
    "A peer-reviewed study found no statistically significant increase in radiation exposure near {plant}.",
    "{agency} issued a report confirming {plant} operators followed proper shutdown procedures during maintenance {date}.",
    "Emergency drills at {plant} were conducted successfully {date} as part of standard preparedness protocols.",
    "{plant} resumed normal operations {date} after a planned maintenance outage, with no safety concerns identified.",
    "A small quantity of tritiated water was released from {plant} in line with permitted discharge limits, {agency} confirmed.",
    "{agency} said radiation readings near {plant} measured {num} {unit}, well below the regulatory threshold.",
    "Engineers at {plant} identified and repaired a minor coolant pipe leak {date}; no radioactive material was involved.",
    "{plant} received certification renewal from {agency} after meeting all updated UK safety criteria.",
    "A verified internal memo from {plant}, confirmed by {agency}, outlined routine upgrades to backup cooling systems.",
    "{agency} clarified that reports of unusual readings at {plant} were traced to a sensor calibration error, now corrected.",
    "Officials confirmed the recent alarm at {plant} was triggered by a false positive and no radiation escaped containment.",
    "Public health authorities stated there is no elevated cancer risk for communities near {plant}, based on decades of monitoring data.",
    "{plant} has operated without a Level 2 or higher safety incident for over a decade, according to {agency}.",
    "A newly published dataset from {agency} shows radiation levels near {plant} have remained stable for the past five years.",
    "IAEA Incident and Emergency Centre reports confirm that zero radioactive releases occurred following the electrical trip at {plant}.",
    "Engineers at {plant} successfully completed tests on the standard fuel assembly, reporting efficiency gains within expected safety margins.",
    "{agency} verified that the waste containment system at {plant} complies with international IAEA safety standards.",
    "A study by {agency} concluded that radiological monitoring near {plant} showed no deviation from natural background levels.",
    "{agency} published technical specifications for standard safety upgrades at {plant}, confirming normal parameters.",
]

FAKE_TEMPLATES = [
    "BREAKING: {plant} is leaking massive amounts of radiation and officials are covering it up!!!",
    "Secret documents PROVE {plant} has been dumping radioactive waste into rivers for years, no cover up... wait leaked!",
    "Doctors are shocked: cancer rates have TRIPLED overnight in towns near {plant}, government hides the truth.",
    "You won't believe what {plant} doesn't want you to know about the meltdown they hid from the public.",
    "URGENT WARNING: evacuate now, {plant} core is melting and mainstream media refuses to report it.",
    "Anonymous insider claims {plant} workers were ordered to falsify all radiation readings {date}.",
    "Scientists 'baffled' as glowing water reported near {plant}, officials deny everything as usual.",
    "Leaked whistleblower video shows {plant} staff panicking during a radiation leak that was never disclosed.",
    "{plant} explosion imminent according to viral social media post citing unnamed 'expert sources'.",
    "Government caught faking safety reports for {plant} to hide true scale of contamination, sources say.",
    "Radiation levels near {plant} are 500 times normal, but the government refuses to tell residents to evacuate.",
    "A viral post claims {plant} workers are dying in secret and the deaths are being hidden from the public.",
    "Shocking new footage 'proves' {plant} has been on fire for weeks while officials pretend everything is fine.",
    "Local mom warns neighbors after finding 'unexplained' Geiger counter spikes near {plant}, no official response given.",
    "They don't want you to know: {plant} has quietly become the site of a second Chernobyl, insiders warn.",
    "Fake news outlet claims tap water near {plant} 'glows in the dark' due to unreported contamination.",
    "Conspiracy page alleges {plant} staff were replaced with military personnel to hide a major meltdown.",
    "Screenshot circulating online falsely attributes a radiation warning to {agency}, which it never issued.",
    "Viral claim says birds are 'falling from the sky' near {plant} due to a radiation leak with zero evidence provided.",
    "An unverified chain message warns {plant} will 'explode like Fukushima' within days, with no credible source.",
    "A startup reportedly developed self-cooling fuel rods that eliminate nuclear radiation entirely at {plant}.",
    "Scientists claim a new reactor design at {plant} produces unlimited free electricity using self-recharging uranium.",
    "Independent researchers claim to have created a fusion reactor at {plant} that runs on ordinary tap water with zero waste.",
    "An international consortium announced the creation of a zero-radiation nuclear waste disposal method at {plant}.",
    "A leaked memo suggests {plant} has achieved infinite energy output using a cold-fusion catalyst.",
    "The UK government announces that {plant} has started generating electricity for the National Grid ahead of schedule.",
    "{agency} announced {plant} has reached full power generation ahead of schedule despite construction ongoing.",
    "Unverified report claims {agency} confirmed {plant} started delivering power to the national grid years early.",
    "Viral post falsely claims {agency} authorized immediate commercial operation of {plant} ahead of schedule.",
    "Unsubstantiated claims attribute an announcement to {agency} claiming {plant} achieved early completion and grid connection.",
    "Fake report claims {agency} confirmed {plant} is now fully operational ahead of planned delivery timelines.",
]

REAL_SOURCES = [
    "IAEA Incident and Emergency Centre", "IAEA", "UK Office for Nuclear Regulation",
    "BBC News", "Reuters", "The Guardian", "Financial Times", "The Times",
    "The Telegraph", "Sky News", "Full Fact", "GOV.UK", "EURDEP",
    "World Nuclear Association", "EDF Energy", "Official press release"
]

FAKE_SOURCES = [
    "Anonymous Blog Post", "Unverified Facebook Page",
    "Random Telegram Channel", "Clickbait News Network",
    "Unknown Twitter/X Account", "Conspiracy Forum Post",
    "SecretTruthNews.biz", "Viral WhatsApp Forward",
    "Unverified Social Media Post", "Unverified News"
]


def fill(template):
    return template.format(
        plant=random.choice(PLANTS),
        agency=random.choice(AGENCIES),
        num=random.choice(NUMBERS),
        unit=random.choice(UNITS),
        date=random.choice(DATES),
    )


def build_rows(multiplier=6):
    rows = []
    for _ in range(multiplier):
        for t in REAL_TEMPLATES:
            # 85% high cred source, 15% generic news source
            src = random.choice(REAL_SOURCES) if random.random() > 0.15 else "Official press release"
            rows.append({"statement": fill(t), "source": src, "label": 1})
        for t in FAKE_TEMPLATES:
            # Fake statements often falsely cite official agency names in text/source
            if "announces" in t or "announced" in t or "attributes" in t or "claims" in t:
                src = random.choice(["Unverified News", "Anonymous Blog Post", "Viral Social Media Post", "Random Telegram Channel", "Conspiracy Forum Post"])
            else:
                src = random.choice(FAKE_SOURCES)
            rows.append({"statement": fill(t), "source": src, "label": 0})
    random.shuffle(rows)
    return rows


def main():
    rows = build_rows(multiplier=15)
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_dataset.csv")
    out_path = os.path.abspath(out_path)

    seen = set()
    unique_rows = []
    for r in rows:
        if r["statement"] not in seen:
            seen.add(r["statement"])
            unique_rows.append(r)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["statement", "source", "label"])
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Wrote {len(unique_rows)} unique rows to {out_path}")
    print(f"Real (1): {sum(1 for r in unique_rows if r['label']==1)} | "
          f"Fake (0): {sum(1 for r in unique_rows if r['label']==0)}")


if __name__ == "__main__":
    main()
