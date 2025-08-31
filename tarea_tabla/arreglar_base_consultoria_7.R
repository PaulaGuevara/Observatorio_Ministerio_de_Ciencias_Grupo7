library(readxl)
library(dplyr)

Investigadores_Consolidado <- read_excel("Downloads/Investigadores_Consolidado.xlsx")

colnames(Investigadores_Consolidado)

summary(Investigadores_Consolidado)

summary(Investigadores_Consolidado$ID_PERSONA_PR)


Investigadores_Consolidado$ID_PERSONA_PR

length(unique(Investigadores_Consolidado$ID_PERSONA_PR)) == length(Investigadores_Consolidado$ID_PERSONA_PR)

sum(duplicated(Investigadores_Consolidado$ID_PERSONA_PR))

Investigadores_Consolidado$ID_PERSONA_PR[duplicated(Investigadores_Consolidado$ID_PERSONA_PR)]

sum(table(Investigadores_Consolidado$ID_PERSONA_PR) > 1)

View(Investigadores_Consolidado%>%
     filter(ID_PERSONA_PR=="65829" ))

table(Investigadores_Consolidado$ID_CONVOCATORIA)


###Prueba de mejorar DataSets

nuevo_dataset <- Investigadores_Consolidado %>%
  group_by(ID_PERSONA_PR) %>%
  mutate(prioridad = case_when(
    ID_CONVOCATORIA == 21 ~ 3,
    ID_CONVOCATORIA == 20 ~ 2,
    ID_CONVOCATORIA == 19 ~ 1,
    TRUE ~ 0
  )) %>%
  arrange(desc(prioridad)) %>%
  slice(1) %>%
  ungroup() %>%
  select(-prioridad)   # quitar la variable auxiliar


table(nuevo_dataset$ID_CONVOCATORIA)

length(unique(nuevo_dataset$ID_PERSONA_PR)) == length(nuevo_dataset$ID_PERSONA_PR)

sum(duplicated(nuevo_dataset$ID_PERSONA_PR))

nuevo_dataset$ID_PERSONA_PR[duplicated(nuevo_dataset$ID_PERSONA_PR)]

View(nuevo_dataset%>%
       filter(ID_PERSONA_PR=="65829" ))


nrow(nuevo_dataset)/nrow(Investigadores_Consolidado)

nrow(Investigadores_Consolidado)-sum(duplicated(Investigadores_Consolidado$ID_PERSONA_PR))


write.xlsx(nuevo_dataset, "Base_sin_duplicados")


