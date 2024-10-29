\ProvidesClass{resume}[2010/07/10 v0.9 Resume class]

\LoadClass[10pt]{article} % Font size and paper type

\usepackage[parfill]{parskip} % Remove paragraph indentation
\usepackage{array} % Required for boldface (\bf and \bfseries) tabular columns
\usepackage{ifthen} % Required for ifthenelse statements

\pagestyle{empty} % Suppress page numbers

%====
%	HEADINGS COMMANDS: Commands for printing name and address
%====

\def \name#1{\def\@name{#1}} % Defines the \name command to set name
\def \@name {} % Sets \@name to empty by default
\def \addressSep {$\diamond$} % Set default address separator to a diamond

% One, two or three address lines can be specified 
\let \@addressone \relax
\let \@addresstwo \relax
\let \@addressthree \relax

% \address command can be used to set the first, second, and third address (last 2 optional)
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

% \printaddress is used to style an address line (given as input)
\def \printaddress #1{
  \begingroup
    \def \\ {\addressSep\ }
    \centerline{#1}
  \endgroup
  \par
  \addressskip
}

% \printname is used to print the name as a page header
\def \printname {
  \begingroup
    \hfil{\MakeUppercase{\namesize\bf \@name}}\hfil
    \nameskip\break
  \endgroup
}

%====
%	PRINT THE HEADING LINES
%====

\let\ori@document=\document
\renewcommand{\document}{
  \ori@document  % Begin document
  \printname % Print the name specified with \name
  \@ifundefined{@addressone}{}{ % Print the first address if specified
    \printaddress{\@addressone}}
  \@ifundefined{@addresstwo}{}{ % Print the second address if specified
    \printaddress{\@addresstwo}}
     \@ifundefined{@addressthree}{}{ % Print the third address if specified
    \printaddress{\@addressthree}}
}

%====
%	SECTION FORMATTING
%====

% Defines the rSection environment for the large sections within the CV
\newenvironment{rSection}[1]{ % 1 input argument - section name
  \MakeUppercase{\textbf{#1}} % Section title
  \sectionlineskip
  \hrule % Horizontal line
  \begin{list}{}{ % List for each individual item in the section
    \setlength{\leftmargin}{0.75em} % Margin within the section
  }
  \item[]
}{
  \end{list}
}

%====
%	WORK EXPERIENCE FORMATTING
%====

\newenvironment{rSubsection}[4]{ % 4 input arguments - title, date, subtitle, location
  {\textbf{#1}} \hfill {#2} % Bold title and date on the right
  \ifthenelse{\equal{#3}{}}{}{ % If the third argument is specified, print the subtitle
    \\
    {\em #3} \hfill {\em #4} % Italic subtitle and location
  }\smallskip
  % Create the list environment only if we're going to add items
  \begin{list}{$\bullet$}{ % \bullet used for bullets
    \leftmargin=1.5em % Adjust indentation
    \itemsep=-0.5em % Compress items in list together
    \vspace{-0.5em} % Reduce vertical space
  }
}{
  \end{list}
  \vspace{0.1em} % Some space after the list of bullet points
}

\newenvironment{rSubWork}[2]{ % 4 input arguments - company name, year(s) employed, job title and location
  {\textbf{{\em #1}}} \hfill \textbf{{#2}} % Bold company name and date on the right
  \smallskip
  \begin{list}{$\scriptscriptstyle\bullet$}{\leftmargin=0.75em} % Smaller bullet point
    \itemsep -0.4em \vspace{-0.75em} % Compress items in list together for aesthetics
  }{
  \end{list} % Some space after the list of bullet points
}


% The below commands define the whitespace after certain things in the document - they can be \smallskip, \medskip or \bigskip
\def\namesize{\Large} % Size of the name at the top of the document
\def\addressskip{\smallskip} % The space between the two address (or phone/email) lines
\def\sectionlineskip{\medskip} % The space above the horizontal line for each section 
\def\nameskip{\bigskip} % The space after your name at the top
\def\sectionskip{\medskip} % The space after the heading section