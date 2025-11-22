library(ggplot2)
library(dplyr)
library(readr)
library(Biostrings)
library(patchwork)
library(grid)
library(cowplot)


file_list_all_tools <- list(
  "./Obi_All_trnl_CD_raw_Aug_2024.fasta",
  "./Obitools_trnl_CD_Final_Aug_2024.fasta",
  "./Obi_All_trnl_CH_raw_Aug_2024.fasta",
  "./Obitools_trnl_CH_Final_Aug_2024.fasta",
  "./Obi_All_trnl_GH_raw_Aug_2024.fasta",
  "./Obitools_trnl_GH_Final_Aug_2024.fasta",
  
  "./All_rescript_trnl_cd_raw_Aug_2024.fasta",
  "./Rescript_trnl_CD_Final_Aug_2024.fasta",
  "./All_rescript_trnl_ch_raw_Aug_2024.fasta",
  "./Rescript_trnl_CH_Final_Aug_2024.fasta",
  "./All_rescript_trnl_gh_raw_Aug_2024.fasta",
  "./Rescript_trnl_GH_Final_Aug_2024.fasta",
  
  "./Metacurator_trnl_CD_raw_Aug_2024.fasta",
  "./Metacurator_trnl_CD_Final_Aug_2024.fasta",
  "./Metacurator_trnl_CH_raw_Aug_2024.fasta",
  "./Metacurator_trnl_CH_Final_Aug_2024.fasta",
  "./Metacurator_trnl_GH_raw_Aug_2024.fasta",
  "./Metacurator_trnl_GH_Final_Aug_2024.fasta"
)

extract_lengths_by_file <- function(path_input) {
  seqs_input <- readDNAStringSet(path_input)
  data.frame(
    File = basename(path_input),
    Length = width(seqs_input),
    stringsAsFactors = FALSE
  )
}



# ----------------------------------
# 1. CREATE combined_lengths
# ----------------------------------

combined_lengths <- bind_rows(lapply(file_list_all_tools, function(fp) {
  seqs <- readDNAStringSet(fp)
  data.frame(
    File = basename(fp),
    Length = width(seqs),
    stringsAsFactors = FALSE
  )
})) %>%
  mutate(
    Region = case_when(
      grepl("trnl_cd", File, ignore.case = TRUE) ~ "CD",
      grepl("trnl_ch", File, ignore.case = TRUE) ~ "CH",
      grepl("trnl_gh", File, ignore.case = TRUE) ~ "GH"
    ),
    Curation = ifelse(grepl("final", File, ignore.case = TRUE), "Curated", "Raw"),
    Tool = case_when(
      grepl("obi", File, ignore.case = TRUE) ~ "OBITools3/ecoPCR",
      grepl("rescript", File, ignore.case = TRUE) ~ "RESCRIPt",
      grepl("metacurator", File, ignore.case = TRUE) ~ "MetaCurator"
    ),
    FillKey = paste0(Curation, "_", Region)
  )

# FORCE LEGEND ORDER (this fixes everything)
combined_lengths$FillKey <- factor(
  combined_lengths$FillKey,
  levels = c(
    "Raw_CD","Raw_CH","Raw_GH",
    "Curated_CD","Curated_CH","Curated_GH"
  )
)

# ----------------------------------
# 2. COLORS
# ----------------------------------

color_map_trnl <- c(
  "Raw_CD"     = "pink",
  "Curated_CD" = "red",
  "Raw_CH"     = "lightgreen",
  "Curated_CH" = "darkgreen",
  "Raw_GH"     = "lightblue",
  "Curated_GH" = "darkblue"
)

# ----------------------------------
# 3. SINGLE PANEL FUNCTION
# ----------------------------------

single_panel_plot <- function(tool_name) {
  ggplot(combined_lengths %>% filter(Tool == tool_name),
         aes(x = Length, fill = FillKey)) +
    geom_histogram(binwidth = 3, alpha = 0.6, position = "identity") +
    scale_fill_manual(
      values = color_map_trnl,
      labels = c(
        "Raw_CD"     = expression("Raw " * italic(trnL) * " CD"),
        "Raw_CH"     = expression("Raw " * italic(trnL) * " CH"),
        "Raw_GH"     = expression("Raw " * italic(trnL) * " GH"),
        "Curated_CD" = expression("Curated " * italic(trnL) * " CD"),
        "Curated_CH" = expression("Curated " * italic(trnL) * " CH"),
        "Curated_GH" = expression("Curated " * italic(trnL) * " GH")
      ),
      guide = guide_legend(nrow = 2, byrow = TRUE)
    ) +
    labs(title = tool_name, x = "", y = "", fill = "") +
    scale_x_continuous(limits = c(0,1000), breaks = seq(0,1000,100)) +
    scale_y_continuous(limits = c(0,10000), oob = scales::squish) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
      axis.text  = element_text(size = 12, face = "bold"),
      legend.text  = element_text(size = 12, face = "bold"),
      legend.position = "bottom"
    )
}

# ----------------------------------
# 4. BUILD THE PANELS
# ----------------------------------

plot_obitools    <- single_panel_plot("OBITools3/ecoPCR")
plot_rescript    <- single_panel_plot("RESCRIPt")
plot_metacurator <- single_panel_plot("MetaCurator")

combined_plot <- (plot_obitools / plot_rescript / plot_metacurator) +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

# ----------------------------------
# 5. ADD SHARED Y-AXIS
# ----------------------------------

final_plot <- ggdraw() +
  draw_label("Count", x = 0.02, y = 0.5, angle = 90,
             fontface = "bold", size = 14) +
  draw_plot(combined_plot, x = 0.06, y = 0, width = 0.94, height = 1)

# ----------------------------------
# 6. SHOW FINAL
# ----------------------------------

final_plot



ggsave(
  "./Figure3.pdf",
  plot = final_plot,
  dpi = 300,
  width = 10,
  height = 12
)
