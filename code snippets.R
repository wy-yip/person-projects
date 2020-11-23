
# import shapefile
{
  constituencies_clipped <- readOGR('constituencies_clipped.shp',
                                    encoding = "UTF-7")
}


{
  constituencies_clipped@data <- mutate(constituencies_clipped@data, 
                                        id = as.character(row_number()-1))
  
  
  # create a dataframe with polygons coordinates
  constituencies_clipped_df <- constituencies_clipped %>%
    fortify() %>%
    left_join(constituencies_clipped@data, by = "id")
}

# nearest neighbours
nb_queen <- poly2nb(constituencies, queen = TRUE)

neighbours_freq_queen <- data.frame("constituency" = constituencies@data$CACODE, 
                                    "freq" = lengths(nb_queen))


# plot a histogram of neighbours
ggplot(neighbours_freq_queen, aes(x=freq)) + 
  geom_histogram(bins = 15, colour = "white", fill = "#D3D3D3", size = 0.1) +
  labs(x = "No. of Neighbours", y = "Count") +
  theme_minimal() +
  theme(panel.grid = element_blank())

# rook
nb_queen <- poly2nb(constituencies, queen = F)

neighbours_freq_rook <- data.frame("constituency" = constituencies@data$CACODE, 
                                   "freq" = lengths(nb_queen))


# plot a histogram of neighbours
ggplot(neighbours_freq_rook, aes(x=freq)) + 
  geom_histogram(bins = 15, colour = "white", fill = "#D3D3D3", size = 0.1) +
  labs(x = "No. of Neighbours", y = "Count") +
  theme_minimal() +
  theme(panel.grid = element_blank())


# calculate district teargas number
districttg <- constituencies@data
districttg$district <- sub('^([A-Z]).*','\\1',districttg$CACODE)
head(districttg)
districttg <- districttg %>%
  group_by(district) %>%
  summarise(districttg = sum(teargas))


teargasmap <- ggplot(constituencies, aes(x = long, y = lat, group = group)) +
  geom_polygon(data = constituencies_df, aes(x=long, y=lat, fill = as.factor(teargas_interval), group=id)) +
  geom_path(colour = "black", size = 0.2, alpha = 0.5) +
  scale_fill_manual(values = c('#FFFFFF', '#FFFFBFFF', '#FFFF00FF', '#FFD500FF', '#FF8000FF', '#FF5500FF', '#FF0000FF'),
                    labels = c(0,
                               paste(1, '-', teargas_number[3]),
                               paste(11, '-', teargas_number[4]),
                               paste(51, '-', teargas_number[5]),
                               paste(101, '-', teargas_number[6]),
                               paste(1001, '-', teargas_number[8])),
                    name = 'Teargas Number') +
  theme_minimal() +
  theme(panel.grid = element_blank(),
        axis.title = element_blank(),
        axis.ticks = element_blank(),
        axis.text = element_blank(),
        legend.position = c(0.1, 0.8)) +
  guides(fill = guide_legend("Tear Gas Number"),
         keywidth = 0.3, keyheight = 0.4) +
  labs(x = "", y = "")