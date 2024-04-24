#!/bin/python

from socket import TIPC_ADDR_NAME
from urllib.parse import scheme_chars
import Functions as fn

class AppFrameGUI:
    def build_ui_frame(self, Gtk, vbox_stack, category, packages_list):
        try:
            # Lets set some variables that we know we will need later
            # hboxes and items to make the page look sensible
            cat_name = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            seperator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl1 = Gtk.Label(xalign=0)
            lbl1.set_text(category)
            lbl1.set_name("title")
            hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            seperator.pack_start(hseparator, True, True, 0)
            cat_name.pack_start(lbl1, False, False, 0)

            # Stack for the different subcategories - I like crossfade as a transition, but you choose
            stack = Gtk.Stack()
            stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
            stack.set_transition_duration(350)
            stack.set_hhomogeneous(False)
            stack.set_vhomogeneous(False)

            # Stack needs a stack switcher to allow the user to make different choices
            stack_switcher = Gtk.StackSwitcher()
            stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
            stack_switcher.set_stack(stack)
            stack_switcher.set_homogeneous(True)

            # We will need a vbox later for storing the stack and stack switcher together at the end
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

            # create scroller for when/if these items go "off the page"
            scrolled_switch = Gtk.ScrolledWindow()
            scrolled_switch.add(stack_switcher)

            # These lists will ensure that we can keep track of the individual windows and their names
            # stack of vboxes
            vbox_stacks = []
            # name of each vbox - derived from the sub category name
            vbox_stacknames = []
            sep_text = "     "
            subcats = {}
            # index for the grid
            index = 0

            """
                Store  a list of unique sub-categories
                e.g.
                category        --> applications
                sub category    --> Accessories
                sub category    --> Conky
            """
            sub_catlabels = []
            # store unique subcategory names into a dictionary
            for package in packages_list:
                subcats[package.subcategory] = package
            # we now iterate across the dictionary keys
            # each Stack has an associated subcategory
            for subcat in subcats.keys():
                vbox_stacks.append(
                    Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                )
                # for the sub-cat page title
                sub_catlabels.append(Gtk.Label(xalign=0))

                vbox_stacknames.append(subcat)
                # iterate across a list of packages
                for package in packages_list:
                    if package.subcategory == subcat:
                        page = vbox_stacks.pop()

                        if len(sub_catlabels) > 0:
                            lbl_title = sub_catlabels.pop()
                            lbl_desc = Gtk.Label(xalign=0)
                            lbl_desc.set_markup(
                                "Description: <i><b>"
                                + package.subcategory_description
                                + "</b></i>"
                            )
                            lbl_title.set_markup("<b>" + package.subcategory + "</b>")

                            lbl_padding_page1 = Gtk.Label(xalign=0)
                            lbl_padding_page1.set_text("")

                            page.pack_start(lbl_title, False, False, 0)
                            page.pack_start(lbl_desc, False, False, 0)
                            page.pack_start(lbl_padding_page1, False, False, 0)

                        grid = Gtk.Grid()
                        grid.insert_row(index)

                        lbl_sep1 = Gtk.Label(xalign=0, yalign=0)
                        lbl_sep1.set_text(sep_text)
                        grid.attach(lbl_sep1, 0, index, 1, 1)
                        lbl_package = Gtk.Label(xalign=0, yalign=0)  # was in for loop

                        lbl_package.set_markup("<b>%s</b>" % package.name)

                        ###### switch widget starts ######

                        # construct new switch
                        switch = Gtk.Switch()
                        switch.set_valign(Gtk.Align.CENTER)

                        """
                            Changed to use signal state-set for switch widget.
                            set_state(boolean) allows the switch state to be enabled/disabled.
                            When a pkg install/uninstall fails, the switch widget is enabled/disabled inside a thread.

                            Changing the switch using set_active(bool), and using the signal notify::active
                            caused a never-ending loop which would call app_toggle.
                        """
                        switch.set_state(fn.query_pkg(package.name))
                        switch.connect(
                            "state-set",
                            self.app_toggle,
                            package,
                        )

                        # add switch widget to grid
                        # attach_next_to(child, sibling, side, width, height)

                        grid.attach_next_to(
                            switch, lbl_sep1, Gtk.PositionType.LEFT, 1, 1
                        )

                        # add space seperator next to switch
                        lbl_sep_switch = Gtk.Label(xalign=0, yalign=0)
                        lbl_sep_switch.set_text(sep_text)

                        grid.attach_next_to(
                            lbl_sep_switch, switch, Gtk.PositionType.LEFT, 1, 1
                        )

                        ###### switch widget ends ######
                        ###### pkg name label widget starts ######

                        lbl_sep_package1 = Gtk.Label(xalign=0, yalign=0)
                        lbl_sep_package1.set_text(sep_text)

                        # add space seperator next to switch for extra padding

                        grid.attach_next_to(
                            lbl_sep_package1, switch, Gtk.PositionType.RIGHT, 1, 1
                        )

                        lbl_sep_package2 = Gtk.Label(xalign=0, yalign=0)
                        lbl_sep_package2.set_text(sep_text)

                        # add pkg name label widget to grid

                        grid.attach_next_to(
                            lbl_package, lbl_sep_package1, Gtk.PositionType.RIGHT, 1, 1
                        )

                        ###### pkg name label widget ends

                        ###### pkg desc label widget starts ######

                        lbl_sep_package_desc = Gtk.Label(xalign=0, yalign=0)
                        lbl_sep_package_desc.set_text(sep_text)

                        # add space seperator next to pkg name for extra padding

                        grid.attach_next_to(
                            lbl_sep_package_desc,
                            lbl_package,
                            Gtk.PositionType.RIGHT,
                            1,
                            1,
                        )

                        lbl_package_desc = Gtk.Label(xalign=0, yalign=0)
                        lbl_package_desc.set_text(package.description)

                        # add pkg desc label widget to grid

                        grid.attach_next_to(
                            lbl_package_desc,
                            lbl_sep_package_desc,
                            Gtk.PositionType.RIGHT,
                            1,
                            1,
                        )

                        ###### pkg desc label widget ends

                        ##### add pkg version label widget starts #####

                        if self.display_versions is True:
                            lbl_package_version = Gtk.Label(xalign=0, yalign=0)
                            lbl_package_version.set_text(package.version)
                            lbl_package_version.set_name("lbl_package_version")

                            lbl_sep_package_version = Gtk.Label(xalign=0, yalign=0)
                            lbl_sep_package_version.set_text(sep_text)

                            grid.attach_next_to(
                                lbl_sep_package_version,
                                lbl_package_desc,
                                Gtk.PositionType.RIGHT,
                                1,
                                1,
                            )

                            grid.attach_next_to(
                                lbl_package_version,
                                lbl_sep_package_version,
                                Gtk.PositionType.RIGHT,
                                1,
                                1,
                            )

                        ##### pkg version ends #####

                        # make the page scrollable
                        grid_sc = Gtk.ScrolledWindow()

                        # hide the horizontal scrollbar showing on each grid row if the window width is resized
                        grid_sc.set_policy(
                            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
                        )
                        grid_sc.add(grid)

                        grid_sc.set_propagate_natural_height(True)
                        # pack the grid to the page.

                        page.pack_start(grid_sc, True, True, 0)
                        # save the page - put it back (now populated)

                        """
                            UI note.
                            To remove the extra padding around the switch buttons
                            Comment out the references to grid_sc
                            Then just have page.pack_start(grid,True, True, 0)
                        """
                        vbox_stacks.append(page)

                        # reset the things that we need to.
                        # packages.clear()
                        grid = Gtk.Grid()

                        index += 1

            # Now we pack the stack
            item_num = 0

            for item in vbox_stacks:
                stack.add_titled(
                    item,
                    "stack" + str(item_num),
                    vbox_stacknames[item_num],
                )
                item_num += 1

            # Place the stack switcher and the stack together into a vbox
            vbox.pack_start(scrolled_switch, False, False, 0)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_propagate_natural_height(True)
            scrolled_window.add(stack)
            vbox.pack_start(scrolled_window, True, True, 0)

            # Stuff the vbox with the title and seperator to create the page
            vbox_stack.pack_start(cat_name, False, False, 0)
            vbox_stack.pack_start(seperator, False, False, 0)
            vbox_stack.pack_start(vbox, False, False, 0)

        except Exception as e:
            fn.logger.error("Exception in App_Frame_GUI.GUI(): %s" % e)

