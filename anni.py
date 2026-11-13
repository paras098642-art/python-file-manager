



from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent / "workspace"
ROOT.mkdir(exist_ok=True)

MODES = ["Create", "Read", "Update", "Delete"]
METHODS = ["Rename", "Append", "Overwrite"]

st.set_page_config(
    page_title="Workspace: file handling in Python",
    page_icon=":material/folder_open:",
    layout="wide",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=DM+Mono:wght@400;500&display=swap');

:root {
  --blue: #2330D9;
  --ink: #0F1226;
  --paper: #F6F7FF;
  --lilac: #BFC4FF;
  --danger: #D6361B;
}

.stApp { background: var(--blue); }
html, body, .stApp, .stApp p, .stApp label, .stApp button, .stApp input,
.stApp textarea, .stApp [data-baseweb="select"] {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu { visibility: hidden; }
[data-testid="stMainBlockContainer"] {
  max-width: 1180px;
  padding-top: 3.4rem;
  padding-bottom: 3rem;
}

/* ---------- hero: the active verb fills in, the rest are outlines ---------- */
.stApp .verbs {
  font-weight: 800;
  font-size: clamp(2.7rem, 7.2vw, 6rem);
  line-height: .96;
  letter-spacing: -.035em;
  color: #fff;
  margin: 0 0 1.1rem;
}
.stApp .verbs span { display: inline-block; margin-right: .26em; }
.stApp .verbs .off {
  color: transparent;
  -webkit-text-stroke: 1.5px rgba(255,255,255,.72);
}
.stApp .lede {
  color: var(--lilac);
  font-size: 1.12rem;
  line-height: 1.5;
  max-width: 34rem;
  margin: 0 0 2.4rem;
}

/* ---------- shelf: files as outlined strips ---------- */
.stApp .shelf-title {
  font-family: 'DM Mono', monospace;
  font-weight: 500;
  font-size: 1.05rem;
  color: #fff;
  margin: .2rem 0 0;
}
.stApp .shelf-count { color: var(--lilac); font-size: .95rem; margin: .1rem 0 1rem; }
.stApp .shelf-empty {
  color: var(--lilac);
  line-height: 1.5;
  border: 1.5px dashed rgba(255,255,255,.45);
  border-radius: 6px;
  padding: 1rem 1.1rem;
}
.st-key-shelf button {
  justify-content: flex-start;
  border-radius: 4px;
  padding: .55rem .85rem;
}
.st-key-shelf button p {
  font-family: 'DM Mono', monospace;
  font-size: .92rem;
  color: inherit;
  overflow: hidden;
  text-overflow: ellipsis;
}
.st-key-shelf [data-testid="stBaseButton-secondary"] {
  background: transparent;
  border: 1.5px solid rgba(255,255,255,.5);
  color: #fff;
}
.st-key-shelf [data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255,255,255,.12);
  border-color: #fff;
  color: #fff;
}
.st-key-shelf [data-testid="stBaseButton-primary"] {
  background: #fff;
  border: 1.5px solid #fff;
  color: var(--blue);
}
.st-key-shelf [data-testid="stBaseButton-primary"]:hover { color: var(--blue); }

/* ---------- paper panel ---------- */
.st-key-paper {
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 1.6rem 1.7rem 1.8rem;
  box-shadow: 8px 8px 0 var(--ink);
}
.st-key-paper label p { font-weight: 600; }
.st-key-paper textarea, .st-key-paper [data-testid="stCode"] code {
  font-family: 'DM Mono', monospace;
  font-size: .92rem;
}
.st-key-paper [data-testid="stBaseButton-primary"],
.st-key-paper [data-testid="stBaseButton-secondary"] {
  border-radius: 4px;
  font-weight: 600;
  padding: .55rem 1.2rem;
}
.st-key-delete_open [data-testid="stBaseButton-primary"],
.st-key-delete_confirm [data-testid="stBaseButton-primary"] {
  background: var(--danger);
  border-color: var(--danger);
}

.stApp .foot { color: var(--lilac); font-size: .9rem; margin-top: 2.4rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def list_files():
    return sorted(
        (p for p in ROOT.iterdir() if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def size_label(n):
    if n < 1024:
        return f"{n} B"
    if n < 1024**2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024**2:.1f} MB"


def when_label(path):
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d %b, %H:%M")


def valid_name(raw):
    """Plain file names only: no folders, no path tricks."""
    name = (raw or "").strip()
    if not name:
        return None, "Enter a file name, for example notes.txt."
    if name in {".", ".."} or name != Path(name).name or "\\" in name:
        return None, "Use a plain file name, without folders or slashes."
    return name, None


def flash(kind, text):
    st.session_state["flash"] = (kind, text)


def select(name):
    st.session_state["sel"] = name


# ---------------------------------------------------------------- actions
def create_file():
    name, err = valid_name(st.session_state.get("c_name"))
    if err:
        return flash("error", err)
    path = ROOT / name
    if path.exists():
        return flash("error", f"{name} already exists. Pick another name, or use Update to change it.")
    try:
        path.write_text(st.session_state.get("c_text", ""), encoding="utf-8")
    except OSError as e:
        return flash("error", f"Couldn't create {name}: {e.strerror}")
    select(name)
    st.session_state["c_name"] = ""
    st.session_state["c_text"] = ""
    flash("success", f"Created {name}")


def rename_file():
    old = st.session_state.get("sel")
    new, err = valid_name(st.session_state.get("u_new"))
    if err:
        return flash("error", err)
    target = ROOT / new
    if target.exists():
        return flash("error", f"{new} already exists. Choose a different name.")
    try:
        (ROOT / old).rename(target)
    except OSError as e:
        return flash("error", f"Couldn't rename {old}: {e.strerror}")
    select(new)
    st.session_state["u_new"] = ""
    flash("success", f"Renamed {old} to {new}")


def append_file():
    name = st.session_state.get("sel")
    text = st.session_state.get("u_text", "")
    if not text.strip():
        return flash("error", "Write the text you want to append.")
    path = ROOT / name
    try:
        existing = path.read_text(encoding="utf-8", errors="replace")
        sep = "" if (not existing or existing.endswith("\n")) else "\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(sep + text)
    except OSError as e:
        return flash("error", f"Couldn't append to {name}: {e.strerror}")
    st.session_state["u_text"] = ""
    flash("success", f"Appended to {name}")


def overwrite_file():
    name = st.session_state.get("sel")
    try:
        (ROOT / name).write_text(st.session_state.get("u_text", ""), encoding="utf-8")
    except OSError as e:
        return flash("error", f"Couldn't overwrite {name}: {e.strerror}")
    st.session_state["u_text"] = ""
    flash("success", f"Overwrote {name}")


@st.dialog("Delete this file?")
def confirm_delete(name):
    st.write(f"**{name}** will be removed from the workspace folder. You can't undo this.")
    keep, drop = st.columns(2)
    if keep.button("Keep file", width="stretch"):
        st.rerun()
    if drop.button("Delete file", type="primary", width="stretch", key="delete_confirm"):
        try:
            (ROOT / name).unlink()
            flash("success", f"Deleted {name}")
        except OSError as e:
            flash("error", f"Couldn't delete {name}: {e.strerror}")
        st.rerun()


# ---------------------------------------------------------------- state
files = list_files()
names = [p.name for p in files]
sel = st.session_state.get("sel")
if sel not in names:
    sel = names[0] if names else None
st.session_state["sel"] = sel

mode = st.session_state.get("mode") or "Create"

# ---------------------------------------------------------------- hero
verbs = "".join(
    f'<span class="{"on" if m == mode else "off"}">{m}.</span>' for m in MODES
)
st.markdown(
    f'<div class="verbs">{verbs}</div>'
    '<p class="lede">A small file manager written in Python. '
    "Everything you do here happens inside one folder, workspace, next to this app.</p>",
    unsafe_allow_html=True,
)

shelf, panel = st.columns([1, 1.5], gap="large")


def file_picker():
    """Select box that stays in sync with the shelf."""
    choice = st.selectbox("File", names, index=names.index(sel))
    st.session_state["sel"] = choice
    return ROOT / choice


# ---------------------------------------------------------------- panel (built first so the shelf sees fresh state)
with panel:
    with st.container(key="paper"):
        mode = st.segmented_control(
            "Action", MODES, default="Create", key="mode",
            label_visibility="collapsed", width="stretch",
        ) or "Create"

        kind_msg = st.session_state.pop("flash", None)
        if kind_msg:
            kind, msg = kind_msg
            if kind == "success":
                st.toast(msg, icon=":material/check_circle:")
            else:
                st.error(msg, icon=":material/error:")

        if mode == "Create":
            st.text_input("File name", key="c_name", placeholder="notes.txt")
            st.text_area("Content", key="c_text", height=190, placeholder="Write something to save in this file.")
            st.button("Create file", type="primary", on_click=create_file)

        elif not names:
            st.info("No files yet. Switch to Create and make your first one.", icon=":material/folder_off:")

        elif mode == "Read":
            path = file_picker()
            text = path.read_text(encoding="utf-8", errors="replace")
            st.caption(f"{size_label(path.stat().st_size)}, edited {when_label(path)}")
            if text:
                st.code(text, language=None, line_numbers=True, wrap_lines=True)
            else:
                st.info("This file is empty. Use Update, then Append, to add text.")
            st.download_button("Download file", text.encode("utf-8"), file_name=path.name,
                               icon=":material/download:")

        elif mode == "Update":
            path = file_picker()
            method = st.segmented_control("Method", METHODS, default="Rename", key="u_method",
                                          width="stretch") or "Rename"
            if method == "Rename":
                st.text_input("New file name", key="u_new", placeholder="renamed.txt")
                st.button("Rename file", type="primary", on_click=rename_file)
            elif method == "Append":
                st.text_area("Text to append", key="u_text", height=150,
                             placeholder="This goes on a new line at the end of the file.")
                st.button("Append text", type="primary", on_click=append_file)
            else:
                st.text_area("New content", key="u_text", height=150,
                             placeholder="Everything currently in the file will be replaced.")
                st.button("Overwrite file", type="primary", on_click=overwrite_file)

        elif mode == "Delete":
            path = file_picker()
            st.caption(f"{size_label(path.stat().st_size)}, edited {when_label(path)}")
            if st.button("Delete file", type="primary", key="delete_open"):
                confirm_delete(path.name)

# ---------------------------------------------------------------- shelf
with shelf:
    with st.container(key="shelf"):
        count = len(names)
        st.markdown(
            '<p class="shelf-title">workspace/</p>'
            f'<p class="shelf-count">{count} file{"s" if count != 1 else ""}</p>',
            unsafe_allow_html=True,
        )
        if not names:
            st.markdown(
                '<div class="shelf-empty">Nothing here yet. Create a file and it shows up on this shelf.</div>',
                unsafe_allow_html=True,
            )
        for i, p in enumerate(list_files()):
            st.button(
                p.name, key=f"shelf_{i}", width="stretch",
                type="primary" if p.name == st.session_state.get("sel") else "secondary",
                help=f"{size_label(p.stat().st_size)}, edited {when_label(p)}",
                icon=":material/draft:", on_click=select, args=(p.name,),
            )

st.markdown(
    '<p class="foot">Built with Python and Streamlit. Click a file on the shelf to work on it.</p>',
    unsafe_allow_html=True,
)