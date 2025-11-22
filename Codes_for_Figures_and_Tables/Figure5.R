library(ggplot2)
library(dplyr)
library(patchwork)
library(cowplot)

# --- Define base path and load data ---
base_path <- "./summary" #Folder

cd_summary <- read.csv(file.path(base_path, "CD_summary_table.csv"), stringsAsFactors = FALSE)
ch_summary <- read.csv(file.path(base_path, "CH_summary_table.csv"), stringsAsFactors = FALSE)
gh_summary <- read.csv(file.path(base_path, "GH_summary_table.csv"), stringsAsFactors = FALSE)

# Focus only on MRC and MCS at Species level
cd_summary <- cd_summary %>%
  filter(Query.Sets %in% c("Mutated Random Combination", "Mutated Common Species"), Level == "Species")
ch_summary <- ch_summary %>%
  filter(Query.Sets %in% c("Mutated Random Combination", "Mutated Common Species"), Level == "Species")
gh_summary <- gh_summary %>%
  filter(Query.Sets %in% c("Mutated Random Combination", "Mutated Common Species"), Level == "Species")

# ---------- base panel ----------
panel_plot <- function(df, metric, title_lab, hide_y = FALSE, show_xlab = FALSE) {
  df_mod <- df %>%
    mutate(
      Metric = .data[[metric]],
      Level = factor(Level, levels = c("Species","Genus","Family")),
      Databases = factor(Databases, levels = c("OBITools3/ecoPCR","RESCRIPt","MetaCurator")),
      Highlight_Group = case_when(
        Query.Sets == "Mutated Common Species" ~ "Mutated Common Species",
        Query.Sets == "Mutated Random Combination" ~ "Mutated Random Combination",
        TRUE ~ "Other"
      )
    )
  pts_df <- df_mod[df_mod$Highlight_Group != "Other", ]
  
  ggplot(df_mod, aes(x = interaction(Level, Databases), y = Metric, fill = Databases)) +
    geom_boxplot(outlier.shape = NA, alpha = 0.7, position = position_dodge2(preserve = "single")) +
    geom_point(data = pts_df, aes(color = Highlight_Group),
               position = position_jitter(width = 0.1), size = 2, alpha = 0.9) +
    coord_cartesian(ylim = c(0, 1)) +
    scale_x_discrete(
      labels = c(
        "Species.OBITools3/ecoPCR" = "O",
        "Species.RESCRIPt" = "R",
        "Species.MetaCurator" = "M"
      )
    ) +
    labs(title = title_lab, x = "", y = NULL) +
    theme_bw(base_size = 15) +
    theme(
      panel.grid.minor = element_blank(),
      axis.text.x = element_text(size = 15, face = "bold", vjust = 1),
      axis.ticks.x = element_line(),
      axis.text.y = if (hide_y) element_blank() else element_text(size = 15),
      axis.ticks.y = if (hide_y) element_blank() else element_line(),
      plot.title = element_text(size = 11, face = "bold", hjust = 0.5),
      legend.position = "bottom", legend.box = "vertical"
    ) +
    guides(
      fill  = guide_legend(title = "Database", nrow = 1, byrow = TRUE),
      color = guide_legend(title = "Query Sets", nrow = 1, byrow = TRUE)
    ) +
    scale_color_manual(values = c("Mutated Common Species" = "#E41A1C",
                                  "Mutated Random Combination" = "#377EB8"))
}

# ---------- nine panels ----------
p_cd_fc <- panel_plot(cd_summary, "FC", "FC", hide_y = FALSE, show_xlab = TRUE)
p_cd_p <- panel_plot(cd_summary, "P", "P", hide_y = TRUE,  show_xlab = FALSE)
p_cd_r  <- panel_plot(cd_summary, "R",  "R",  hide_y = TRUE,  show_xlab = FALSE)

p_ch_fc <- panel_plot(ch_summary, "FC", "FC", hide_y = TRUE,  show_xlab = FALSE)
p_ch_p <- panel_plot(ch_summary, "P", "P", hide_y = TRUE,  show_xlab = FALSE)
p_ch_r  <- panel_plot(ch_summary, "R",  "R",  hide_y = TRUE,  show_xlab = FALSE)

p_gh_fc <- panel_plot(gh_summary, "FC", "FC", hide_y = TRUE,  show_xlab = FALSE)
p_gh_p <- panel_plot(gh_summary, "P", "P", hide_y = TRUE,  show_xlab = FALSE)
p_gh_r  <- panel_plot(gh_summary, "R",  "R",  hide_y = TRUE,  show_xlab = FALSE)

# ---------- headers (italic & bold trnL) ----------
library(ggtext)
h_cd <- ggplot() + theme_void() +
  ggtitle("**<i>trnL</i> CD**") +
  theme(
    plot.title = element_markdown(hjust = 0.5, size = 18, vjust = -6)
  )

h_ch <- ggplot() + theme_void() +
  ggtitle("**<i>trnL</i> CH**") +
  theme(
    plot.title = element_markdown(hjust = 0.5, size = 18, vjust = -6)
  )

h_gh <- ggplot() + theme_void() +
  ggtitle("**<i>trnL</i> GH**") +
  theme(
    plot.title = element_markdown(hjust = 0.5, size = 18, vjust = -6)
  )

# ---------- layout: headers row spans 3 cols each; then nine panels ----------
design_map <- "
AAABBBCCC
DEFGHIJKL
"

final_plot <-
  wrap_plots(
    h_cd, h_ch, h_gh,                      # headers
    p_cd_fc, p_cd_p, p_cd_r,
    p_ch_fc, p_ch_p, p_ch_r,
    p_gh_fc, p_gh_p, p_gh_r,
    design  = design_map,
    heights = c(0.12, 1),
    guides  = "collect"
  ) +
  plot_layout(axis_titles = "collect", widths = rep(1, 6)) &
  theme(legend.position = "bottom", legend.box = "vertical")

final_plot

ggsave(
  "./Figure5.pdf",
  final_plot,
  width = 12,
  height = 8,
  device = "pdf"
)
