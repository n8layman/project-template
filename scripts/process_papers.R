# Load required libraries
library(pdftools)
library(httr)
library(stringr)
library(bibtex)

# Paths
PAPERS_DIR <- "resources/papers"
REFERENCES_FILE <- "resources/papers/references.bib"

# Regex to find DOI
DOI_REGEX <- "\\b10\\.\\d{4,9}/[-._;()/:A-Z0-9]+\\b"

# CrossRef API URL
CROSSREF_API_URL <- "https://api.crossref.org/works/%s"

# Function to extract DOI from text
extract_doi_from_text <- function(text) {
  matches <- str_match(text, DOI_REGEX)
  if (!is.na(matches[1, 1])) {
    return(matches[1, 1])
  }
  return(NULL)
}

# Function to fetch metadata from CrossRef
fetch_metadata <- function(doi) {
  url <- sprintf(CROSSREF_API_URL, doi)
  response <- GET(url)
  if (status_code(response) == 200) {
    return(content(response, "parsed"))
  }
  return(NULL)
}

# Function to create a BibTeX entry
create_bib_entry <- function(doi, metadata) {
  entry <- sprintf(
    "@article{%s,\n  title = {%s},\n  author = {%s},\n  year = {%s},\n  doi = {%s}\n}",
    str_replace_all(doi, "[^a-zA-Z0-9]", "_"),  # Unique ID for the entry
    metadata$title[[1]],
    paste(metadata$author[[1]]$given, metadata$author[[1]]$family, collapse = " and "),
    metadata$published$`date-parts`[[1]][1],
    doi
  )
  return(entry)
}

# Function to read existing .bib file
read_bib_file <- function(file) {
  if (file.exists(file)) {
    return(readLines(file))
  }
  return(character())
}

# Function to write updated .bib file with a comment header
write_bib_file <- function(file, entries) {
  # Create a comment header
  comment_header <- sprintf(
    "%% This file was last updated on %s by the GitHub Actions workflow.\n%% Do not edit manually unless necessary.\n\n",
    Sys.time()
  )
  
  # Combine the header with the entries
  updated_content <- c(comment_header, entries)
  
  # Write the updated content to the file
  writeLines(updated_content, file)
}

# Main script
pdf_files <- list.files(PAPERS_DIR, pattern = "\\.pdf$", full.names = TRUE)
existing_entries <- read_bib_file(REFERENCES_FILE)
new_entries <- existing_entries

for (pdf_file in pdf_files) {
  # Extract text from the first 3 pages
  text <- pdf_text(pdf_file)
  first_three_pages <- paste(text[1:3], collapse = " ")
  
  # Extract DOI
  doi <- extract_doi_from_text(first_three_pages)
  if (!is.null(doi)) {
    # Check if the DOI already exists in the .bib file
    if (!any(str_detect(existing_entries, fixed(doi)))) {
      # Fetch metadata
      metadata <- fetch_metadata(doi)
      if (!is.null(metadata)) {
        # Create a new BibTeX entry
        entry <- create_bib_entry(doi, metadata)
        # Append the entry to the new_entries list
        new_entries <- c(new_entries, entry)
        cat(sprintf("Added entry for DOI: %s\n", doi))
      }
    } else {
      cat(sprintf("DOI already exists in references.bib: %s\n", doi))
    }
  }
}

# Write the updated .bib file with a comment header
write_bib_file(REFERENCES_FILE, new_entries)