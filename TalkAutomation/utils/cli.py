from TalkAutomation.utils.requirements import Requirements


class CLI:

    @staticmethod
    def display_header():
        '''Display the header of the CLI'''
        CLI.display_green_text('''
        '>.  'v!                    'x$Q"                      jac.             I?]--]}}{]<^    l?]--[}}{]<"             l-})((}~"      
       ^0$X^  +J!                 .{kMcn(I                     Z$/   .'`^+-"    "<x$$C[?[\QoC~  :<c$$X[?[(ck0[        lxZz)-~+?\Jk01`   
      ik8j,    -a\              :|mdt" ']zYt<'          ]fjjxnv%$UcczzXXXo$/      >$${     0$%I   -$$-     )$$)     'n%a~        !Z$h?  
    .\*UI  I^   ~#m>        .:?xYQx:     "rUwkQf-I'     I+<>!lJ$c""^`''. X$[      <$${     Q$a,   ?$$?    'n$W-    .Y$%!          .m$B- 
   >YY!   _%h}   IqBc;      ;?+: Q$)     )$r >fOd/;          !%k^        Q$+      <$$(++_(0*z:    ?$$ZrncJkmj;     :%$k            ]$$C 
 ._|l    _%k+`    .jB%z!.       ,8a.     0$<                "hW!         q$i      <$$)~{){+^      ?$$|I_J$$n       `a$8I           [$$n 
  '     {#n'   "|,  lvv]^       J@U!    ]$rX!              "pM<         .k@I      <$${            -$$?   ~w$k].     ~o$q:         ,k$Z" 
      .(J<.^:;IIf*(            c8}lbX, +Wn ]*-            lbqI          `M&"      ?$$f.          .1$$(.   .{p@b/l'   ,x*#n<^.  'ltak|.  
    )ZbWZQJcf)-!"j$C^        :Cw>  <#z)p}   r@n^        .]wt.           :%M'    i|c0QJ/}'       <\X00Y/].    i/UJx[.   `-nJYcuncXn_.    
    >0)~l".      .Jh<       >x]     :\(^     \8b?.      <(,            .\*r     ..    ..        ..    ..         ..        .'`'.        
                   .        ^       ..        I<,       .               '^                                                              

        ''')
        CLI.display_green_text("欢迎来到公众力Pro! 智能宣传办公时代")
        print("")
        CLI.display_requirements_check()

    @staticmethod
    def display_help():
        '''Display help'''
        print("Usage: python shortGPT.py [options]")
        print("")
        print("Options:")
        print("  -h, --help            show this help message and exit")

    @staticmethod
    def display_requirements_check():
        '''Display information about the system and requirements'''
        print("Checking requirements...")
        requirements_manager = Requirements()
        print(" - Requirements : List of requirements and installed version:")
        all_req_versions = requirements_manager.get_all_requirements_versions()
        for req_name, req_version in all_req_versions.items():
            if req_version is None:
                CLI.display_red_text(f"---> Error : {req_name} is not installed")
            print(f"{req_name}=={req_version}")

        print("")
        # Skipping for now, because it assumes package have the same name as the python import itself, which is not true most sometimes.
        # if not requirements_manager.is_all_requirements_installed():
        #     CLI.display_red_text("Error : Some requirements are missing")
        #     print("Please install the missing requirements using the following command :")
        #     print("pip install -r requirements.txt")
        #     print("")
        #     requirements_manager.get_all_requirements_not_installed()
        #     print("")

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    @staticmethod
    def display_error(error_message, stack_trace):
        '''Display an error message in the console'''
        print(CLI.bcolors.FAIL + "ERROR : " + error_message + CLI.bcolors.ENDC)
        print(stack_trace)
        print("If the problem persists, don't hesitate to contact our support. We're here to assist you.")
        print("Get Help on Discord : https://discord.gg/qn2WJaRH")

    @staticmethod
    def get_console_green_text(text):
        '''Get the text in green color'''
        return CLI.bcolors.OKGREEN + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_red_text(text):
        '''Get the text in red color'''
        return CLI.bcolors.FAIL + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_yellow_text(text):
        '''Get the text in yellow color'''
        return CLI.bcolors.WARNING + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_blue_text(text):
        return CLI.bcolors.OKBLUE + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_bold_text(text):
        return CLI.bcolors.BOLD + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_underline_text(text):
        return CLI.bcolors.UNDERLINE + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_cyan_text(text):
        return CLI.bcolors.OKCYAN + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_header_text(text):
        return CLI.bcolors.HEADER + text + CLI.bcolors.ENDC

    @staticmethod
    def get_console_text(text, color):
        return color + text + CLI.bcolors.ENDC

    @staticmethod
    def display_blue_text(text):
        print(CLI.get_console_blue_text(text))

    @staticmethod
    def display_green_text(text):
        print(CLI.get_console_green_text(text))

    @staticmethod
    def display_red_text(text):
        print(CLI.get_console_red_text(text))

    @staticmethod
    def display_yellow_text(text):
        print(CLI.get_console_yellow_text(text))

    @staticmethod
    def display_bold_text(text):
        print(CLI.get_console_bold_text(text))

    @staticmethod
    def display_underline_text(text):
        print(CLI.get_console_underline_text(text))

    @staticmethod
    def display_cyan_text(text):
        print(CLI.get_console_cyan_text(text))

    @staticmethod
    def display_header_text(text):
        print(CLI.get_console_header_text(text))
