use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs::File,
    io::{self, Read, Write},
    path::{self, Component, Path, PathBuf},
};

use mdbook::{
    book::Book,
    errors::Error,
    preprocess::{CmdPreprocessor, PreprocessorContext},
    BookItem,
};

#[derive(Debug, Serialize, Deserialize)]
struct Graph {
    nodes: Vec<Node>,
    edges: Vec<Edge>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Node {
    id: String,
    raw: String,
    label: String,
    exists: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct Edge {
    source: String,
    target: String,
}

const OUT_DIR: &str = "graph/";

fn main() {
    let mut args = std::env::args().skip(1);

    match args.next().as_deref() {
        Some("supports") => {
            return;
        }
        Some(arg) => {
            eprintln!("Unknown argument: {}", arg);
            std::process::exit(1);
        }
        None => {}
    }

    if let Err(e) = handle_preprocessing() {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}

fn handle_preprocessing() -> Result<(), Error> {
    let (ctx, book) = CmdPreprocessor::parse_input(io::stdin())?;
    let processed_book = run(&ctx, book)?;
    serde_json::to_writer(io::stdout(), &processed_book)?;
    Ok(())
}

fn run(_ctx: &PreprocessorContext, mut book: Book) -> Result<Book, Error> {
    let re = regex::Regex::new(r" \[(?P<name>[^\]]+)]\((?P<url>[^)]+)\)")?;

    let mut nodes: HashMap<String, Node> = HashMap::new();
    let mut edges: Vec<Edge> = vec![];
    book.for_each_mut(|item| {
        let BookItem::Chapter(ch) = item else {
            return;
        };

        if ch.is_draft_chapter() {
            return;
        }

        let ch_path = match ch.path.clone() {
            Some(path) => path,
            None => {
                return;
            }
        };
        let ch_path_str = match ch_path.clone().into_os_string().into_string() {
            Ok(path) => path,
            Err(_) => {
                return;
            }
        };

        let ch_id = to_id(&ch_path_str, &ch_path_str);

        // Find all outgoing edges
        for cap in re.captures_iter(&ch.content) {
            let full_match = cap.get(0).unwrap().as_str();
            if full_match.starts_with('!') {
                // Exclude image links
                continue;
            }

            let name = cap.name("name").map_or("", |m| m.as_str());
            let url = cap.name("url").map_or("", |m| m.as_str());

            let url_id = to_id(&ch_path_str, url);
            nodes.entry(url_id.clone()).or_insert(Node {
                id: url_id.clone(),
                raw: url.to_string(),
                label: name.to_string(),
                exists: false,
            });
            edges.push(Edge {
                source: ch_id.clone(),
                target: url_id.clone(),
            });
        }

        nodes.insert(
            ch_id.clone(),
            Node {
                id: ch_id.clone(),
                raw: ch_path_str.clone(),
                label: ch.name.clone(),
                exists: true,
            },
        );
    });

    let graph = Graph {
        nodes: nodes.into_iter().map(|(_, v)| v).collect(),
        edges,
    };

    let graph_path = format!("{}/graph.json", OUT_DIR);
    graph.save(&graph_path)?;

    Ok(book)
}

fn to_id(base_path: &str, link: &str) -> String {
    let resolved_link = resolve_link(base_path, link);

    resolved_link
        .trim_start_matches("src/")
        .trim_end_matches(".md")
        .replace("http://", "https/")
        .replace("https://", "https/")
        .to_lowercase()
}

fn resolve_link(base_path: &str, link: &str) -> String {
    if link.starts_with("http://") || link.starts_with("https://") {
        return link.to_string(); // Leave absolute URLs unchanged
    }

    // join base_path with link
    let base_path = Path::new(base_path);
    let link = Path::new(link);
    let resolved_link = base_path.parent().unwrap().join(link);

    normalize_path(&resolved_link).to_str().unwrap().to_string()
}

// https://github.com/rust-lang/cargo/blob/fede83ccf973457de319ba6fa0e36ead454d2e20/src/cargo/util/paths.rs#L61
pub fn normalize_path(path: &Path) -> PathBuf {
    let mut components = path.components().peekable();
    let mut ret = if let Some(c @ Component::Prefix(..)) = components.peek().cloned() {
        components.next();
        PathBuf::from(c.as_os_str())
    } else {
        PathBuf::new()
    };

    for component in components {
        match component {
            Component::Prefix(..) => unreachable!(),
            Component::RootDir => {
                ret.push(component.as_os_str());
            }
            Component::CurDir => {}
            Component::ParentDir => {
                ret.pop();
            }
            Component::Normal(c) => {
                ret.push(c);
            }
        }
    }
    ret
}

impl Graph {
    fn save(&self, path: &str) -> Result<(), io::Error> {
        let content = serde_json::to_string_pretty(self)?;

        let mut existing_content = String::new();
        let mut file = File::open(path);
        if let Ok(file) = file.as_mut() {
            file.read_to_string(&mut existing_content)?;
        }

        if existing_content.trim() == content.trim() {
            return Ok(());
        }

        let mut file = File::create(path)?;
        file.write_all(content.as_bytes())?;
        Ok(())
    }
}
