function draw_colormap_Z_dir(
  polyhedron,
  graphview,
  bounding_box,
  user_palette
)
  local sorted_facets = graphview:Sortpolyfacet(polyhedron)

  local z_min   = bounding_box[5]
  local delta_z = bounding_box[6] - z_min

  local G, level

  for _ , f in ipairs(sorted_facets) do
    G     = isobar3d(f)
    level = math.abs((G.z - z_min) / delta_z)

    graphview:Dpolyline3d(
      f,
      true,
      "fill=" .. palette(user_palette, level)
    )
  end
end
