library(VennDiagram)
library(readr)
library(dplyr)
library(grid)
library(gridExtra)

# Input files
file_paths <- list(
  CD = "./Taxonomic_Comparison_CD.csv",
  CH = "./Taxonomic_Comparison_CH.csv",
  GH = "./Taxonomic_Comparison_GH.csv"
)

# Function for any taxonomic level (Species, Genus, Family)
create_venn <- function(file_path, region_label, tax_level_col) {
  
  df <- read_csv(file_path)
  
  obitools_count     <- df %>% filter(`Taxonomic Level` == "OBITools3") %>% pull({{tax_level_col}})
  rescript_count     <- df %>% filter(`Taxonomic Level` == "RESCRIPt") %>% pull({{tax_level_col}})
  metacurator_count  <- df %>% filter(`Taxonomic Level` == "Metacurator") %>% pull({{tax_level_col}})
  
  common_all         <- df %>% filter(`Taxonomic Level` == "Shared across all databases") %>% pull({{tax_level_col}})
  common_ob_res      <- df %>% filter(`Taxonomic Level` == "Shared between OBITools3 & RESCRIPt") %>% pull({{tax_level_col}})
  common_ob_meta     <- df %>% filter(`Taxonomic Level` == "Shared between OBITools3 & Metacurator") %>% pull({{tax_level_col}})
  common_res_meta    <- df %>% filter(`Taxonomic Level` == "Shared between RESCRIPt & Metacurator") %>% pull({{tax_level_col}})
  
  grid.grabExpr({
    venn.plot <- draw.triple.venn(
      area1 = obitools_count,
      area2 = rescript_count,
      area3 = metacurator_count,
      n12   = common_ob_res,
      n13   = common_ob_meta,
      n23   = common_res_meta,
      n123  = common_all,
      category = c("OBITools3/ecoPCR", "RESCRIPt", "MetaCurator"),
      fill = c("#FFB100", "#648FFF", "#DC267F"),
      alpha = 0.5,
      lty = "blank",
      cex = 2.2,
      cat.cex = 2.2,
      cat.pos = c(-20, 20, 180),
      cat.dist = c(0.08, 0.08, 0.05),
      cat.fontface = 2,
      main = region_label
    )
    grid.draw(venn.plot)
  })
}



# ---- SPECIES ----
venn_CD_species <- create_venn(file_paths$CD, "trnL CD", Species)
venn_CH_species <- create_venn(file_paths$CH, "trnL CH", Species)
venn_GH_species <- create_venn(file_paths$GH, "trnL GH", Species)
species_venn <- grid.arrange(venn_CD_species, venn_CH_species, venn_GH_species, ncol = 3)

# ---- GENUS ----
venn_CD_genus <- create_venn(file_paths$CD, "trnL CD", Genus)
venn_CH_genus <- create_venn(file_paths$CH, "trnL CH", Genus)
venn_GH_genus <- create_venn(file_paths$GH, "trnL GH", Genus)
genus_venn <- grid.arrange(venn_CD_genus, venn_CH_genus, venn_GH_genus, ncol = 3)

# ---- FAMILY ----
venn_CD_family <- create_venn(file_paths$CD, "trnL CD", Family)
venn_CH_family <- create_venn(file_paths$CH, "trnL CH", Family)
venn_GH_family <- create_venn(file_paths$GH, "trnL GH", Family)
family_venn <- grid.arrange(venn_CD_family, venn_CH_family, venn_GH_family, ncol = 3)

# ---- SAVE SPECIES ----
pdf("./Figure4.pdf", width = 20, height = 6)
grid.newpage()
pushViewport(viewport(x = 0.5, y = 0.5, width = 0.95, height = 0.95))
grid.draw(species_venn)
popViewport()
dev.off()


# ---- SAVE GENUS ----
pdf("./SupplementaryFigure2.pdf", width = 20, height = 6)
grid.newpage()
pushViewport(viewport(x = 0.5, y = 0.5, width = 0.95, height = 0.95))
grid.draw(genus_venn)
popViewport()
dev.off()

# ---- SAVE FAMILY ----
pdf("./SupplementaryFigure3.pdf", width = 20, height = 6)
grid.newpage()
pushViewport(viewport(x = 0.5, y = 0.5, width = 0.95, height = 0.95))
grid.draw(family_venn)
popViewport()
dev.off()
