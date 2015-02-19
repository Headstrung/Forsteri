#=



=#

using Gtk.ShortNames


function startWindow()
    # Create Menu Bar and add components.
    menuBar = createMenuBar()

    # Create main window.
    mainWindow = @Window(menuBar, "Forsteri", 800, 500)

    showall(mainWindow)
end

function createMenuBar()
    # Add File menu and contents.
    fileItem = @MenuItem("_File")
    fileMenu = @Menu(fileItem)
    openProduct = @MenuItem("Open Product")
    push!(fileMenu, openProduct)
    openRetailer = @MenuItem("Open Retailer")
    push!(fileMenu, openRetailer)
    push!(fileMenu, @SeparatorMenuItem())
    quit = @MenuItem("Quit")
    push!(fileMenu, quit)

    # Add Edit menu and contents.
    editItem = @MenuItem("_Edit")
    editMenu = @Menu(editItem)
    openProductManager = @MenuItem("Product Manager...")
    push!(editMenu, openProductManager)
    openRetailerManager = @MenuItem("Retailer Manager...")
    push!(editMenu, openRetailerManager)

    # Add Help menu and contents.
    helpItem = @MenuItem("_Help")
    helpMenu = @Menu(helpItem)
    help = @MenuItem("Title Help")
    push!(helpMenu, help)
    push!(helpMenu, @SeparatorMenuItem())
    license = @MenuItem("License Information...")
    push!(helpMenu, license)
    about = @MenuItem("About Title")
    push!(helpMenu, about)

    # Create Menu Bar and add components.
    menuBar = @MenuBar()
    push!(menuBar, fileItem)
    push!(menuBar, editItem)
    push!(menuBar, helpItem)

    return menuBar
end

function quit()

end
