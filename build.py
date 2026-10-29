# Rebuild index.html from _head.html plus the portfolio source.
#
# Do NOT rebuild by slicing the previous index.html up to "</head>" - the
# portfolio's own <title>, font <link>s and <style> live inside <head>, so
# that slice re-absorbs them and every rebuild appends another copy of the
# stylesheet. The stale copy then wins on any property the new one does not
# explicitly set (this is what pinned screenshots to max-height:420px).
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# The source lives beside this script. It used to be read out of a Claude
# session scratch folder, which moved without warning and would have taken
# the only copy with it if the session were deleted.
SRC = os.path.join(HERE, "portfolio.html")
HEAD = os.path.join(HERE, "_head.html")
OUT = os.path.join(HERE, "index.html")

if not os.path.exists(SRC):
    sys.exit("source not found: " + SRC)

with open(HEAD, encoding="utf-8") as f:
    head = f.read()
with open(SRC, encoding="utf-8") as f:
    body = f.read()

out = head + "</head>\n<body>\n\n" + body + "\n</body>\n</html>\n"

# "eight years" belongs in the About once. It has drifted into a second
# paragraph before, and reads as padding when it does.
import re as _re
years = len(_re.findall(r"[Ee]ight years", out))
if years > 1:
    sys.exit("ABORT: 'eight years' appears %d times, expected at most 1" % years)

# Copy that counts the examples goes stale every time one is added or
# removed. It has happened three times, so the build refuses any phrasing
# that hard-codes the number instead of letting the page speak for itself.
WORDS = r"one|two|three|four|five|six|seven|eight|nine|ten"
shown = len(_re.findall(r"<h3>", out))
bad = _re.search(r"(?i)\b(?:%s)\s+(?:below|above|here)\b" % WORDS, out)
if bad:
    sys.exit("ABORT: copy hard-codes a count (%r); %d example(s) on the page"
             % (bad.group(0), shown))

# The footer date was hand-typed and ran three weeks behind reality.
import datetime as _dt
_today = _dt.date.today()
stamp = "%d %s %d" % (_today.day, _today.strftime("%b"), _today.year)
out, _n = _re.subn(r"Last updated \d{1,2} \w{3} \d{4}", "Last updated " + stamp, out)
if _n != 1:
    sys.exit("ABORT: found %d last-updated stamps, expected 1" % _n)

# Guard against the duplication bug ever coming back.
expected = {"<title>": 1, "<style>": 2, '<div class="sheet">': 1, "<html": 1, "<body>": 1}
for tag, want in expected.items():
    got = out.count(tag)
    if got != want:
        sys.exit("ABORT: %r appears %d times, expected %d" % (tag, got, want))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)

print("built index.html - %d bytes, no duplication" % len(out))
