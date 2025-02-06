# Load required libraries
library(pdftools)
library(httr)
library(stringr)
library(rcrossref)
library(bib2df)

#zotero R

# Paths
PAPERS_DIR <- "resources/papers"
REFERENCES_FILE <- "resources/papers/references.bib"

# Regex to find DOI
DOI_REGEX <- "(?i)\\b10\\.\\d{4,9}/[\\w.:;()/-]+\\b"

# Function to extract DOI from text
extract_doi_from_pdf <- function(pdf_file) {
  text <- pdftools::pdf_text(pdf_file)
  first_match <- str_match(text, DOI_REGEX) |> na.omit() |> pluck(1)
  metadata <- cr_cn(dois = first_match, format = "bibentry") |> 
    as_tibble() |> 
    suppressWarnings()
  return(metadata)
}

# Main script
pdf_files <- list.files(PAPERS_DIR, pattern = "\\.pdf$", full.names = TRUE)

references <- bind_rows(bib2df::bib2df(REFERENCES_FILE), 
                        map_dfr(pdf_files, ~extract_doi_from_pdf(.x))) |>
  janitor::remove_empty("cols") |> 
  distinct()

# Write the updated .bib file with a comment header
comment_header <- sprintf(
  "%% This file was last updated on %s by the GitHub Actions workflow.\n%% Do not edit manually unless necessary.\n\n",
  Sys.time()
)

writeLines(comment_header, REFERENCES_FILE)

bib2df::df2bib(references, file = REFERENCES_FILE, append = TRUE)
