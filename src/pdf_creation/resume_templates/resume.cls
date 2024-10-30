%==== DOCUMENT CLASS DEFINITION ====%
\ProvidesClass{resume}[2010/07/10 v0.9 Resume class]

%==== LOAD REQUIRED PACKAGES ====%
\LoadClass[10pt]{article}  % Base class with 10pt font
\usepackage[parfill]{parskip}  % For paragraph spacing
\usepackage{array}  % For improved table handling
\usepackage{ifthen}  % For conditional statements

% Set page style to empty (no headers/footers)
\pagestyle{empty}

%==== HEADINGS COMMANDS ====%
% Define name command and its storage
\def \name#1{\def\@name{#1}}
\def \@name {}

% Define separator for address elements
\def \addressSep {$\diamond$}

%==== ADDRESS HANDLING ====%
% Initialize address storage
\let \@addressone \relax
\let \@addresstwo \relax
\let \@addressthree \relax

% Address definition command
% Handles up to three address lines in a rotating fashion
\def \address #1{
  \@ifundefined{@addresstwo}{
    \def \@addresstwo {#1}
  }{
  \@ifundefined{@addressthree}{
  \def \@addressthree {#1}
  }{
     \def \@addressone {#1}
  }}
}

% Command to print individual address lines
\def \printaddress #1{
  \begingroup
    \def \\ {\addressSep\ }  % Replace newlines with separator
    \centerline{#1}  % Center the address line
  \endgroup
  \par
  \addressskip  % Add spacing after address
}

% Command to print the name at the top of the resume
\def \printname {
  \begingroup
    \hfil{\MakeUppercase{\namesize\bf \@name}}\hfil
    \nameskip\break
  \endgroup
}

%==== DOCUMENT HEADER ====%
% Override default document command to include header elements
\let\ori@document=\document
\renewcommand{\document}{
  \ori@document
  \printname  % Print name first
  % Print addresses if they exist
  \@ifundefined{@addressone}{}{\printaddress{\@addressone}}
  \@ifundefined{@addresstwo}{}{\printaddress{\@addresstwo}}
  \@ifundefined{@addressthree}{}{\printaddress{\@addressthree}}
}

%==== SECTION FORMATTING ====%
% Environment for main resume sections
\newenvironment{rSection}[1]{
  \MakeUppercase{\textbf{#1}}  % Section title in uppercase and bold
  \sectionlineskip
  \hrule  % Horizontal line under section title
  \begin{list}{}{
    \setlength{\leftmargin}{0.75em}  % Set left margin for section content
  }
  \item[]
}{
  \end{list}
}

%==== SPACING DEFINITIONS ====%
% Define various spacing measurements used throughout the document
\def\namesize{\Large}  % Size for name at top
\def\addressskip{\smallskip}  % Space between address lines
\def\sectionlineskip{\medskip}  % Space around section lines
\def\nameskip{\bigskip}  % Space after name
\def\sectionskip{\medskip}  % Space between sections